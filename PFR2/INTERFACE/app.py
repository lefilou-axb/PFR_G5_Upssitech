"""
Serveur Flask — Interface Web Robot (Raspberry Pi 3B)
=====================================================
À placer dans : /home/groupe5/Documents/PFR/INTERFACE/app.py

Structure attendue sur la Pi :
  /home/groupe5/Documents/PFR/
  ├── INTERFACE/
  │   ├── app.py              ← ce fichier
  │   └── templates/
  │       └── robot_interface.html
  └── TEXT_ENGINE/
      ├── pfr_text.out        ← compilé sur la Pi avec make
      ├── lexique_fr.txt
      ├── lexique_en.txt
      ├── config_lang.txt     ← écrit par Flask avant chaque requête
      └── commands.txt        ← écrit par pfr_text.out, lu par Flask

Pré-requis :
  sudo apt install python3-flask python3-flask-cors python3-serial
  # ou :
  pip3 install flask flask-cors pyserial

Lancement :
  cd /home/groupe5/Documents/PFR/INTERFACE
  python3 app.py

Accès depuis le réseau : http://<IP_du_Pi>:5000
"""

import io
import os
import struct
import subprocess
import threading
import time
import zlib

import serial
import serial.tools.list_ports
from flask import Flask, jsonify, render_template, request, send_file, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════════════════
#  CHEMINS — TOUT EST ABSOLU POUR ÉVITER LES SURPRISES
# ═══════════════════════════════════════════════════

BASE_DIR         = "/home/groupe5/Documents/PFR"
TEXT_ENGINE_DIR  = os.path.join(BASE_DIR, "TEXT_ENGINE")

C_PROGRAM_PATH   = os.path.join(TEXT_ENGINE_DIR, "pfr_text.out")
CONFIG_LANG_FILE = os.path.join(TEXT_ENGINE_DIR, "config_lang.txt")
COMMANDS_FILE    = os.path.join(TEXT_ENGINE_DIR, "commands.txt")

# Carte LiDAR générée par ROS 2
MAP_FILE = "/home/groupe5/ros2_ws/ma_carte.pgm"

# ═══════════════════════════════════════════════════
#  CONFIGURATION SÉRIE
# ═══════════════════════════════════════════════════

SERIAL_PORT = os.environ.get("ROBOT_PORT", "/dev/ttyACM0")
SERIAL_BAUD = 115200

# Délai d'attente entre deux commandes série consécutives (secondes).
# Flask attend la fin d'exécution estimée de chaque commande avant d'envoyer la suivante.
SPEED_M_PER_S   = 0.4    # vitesse rectiligne du robot (à calibrer)
SPEED_DEG_PER_S = 180.0  # vitesse de rotation (à calibrer)

# ═══════════════════════════════════════════════════
#  ÉTAT GLOBAL
# ═══════════════════════════════════════════════════

serial_conn: serial.Serial | None = None
serial_lock = threading.Lock()

# ─── État des capteurs ultrason (mis à jour en arrière-plan) ───
sensor_data: dict = {"s1": None, "s2": None, "s3": None}
sensor_lock = threading.Lock()


def _serial_reader_thread():
    """
    Lit en continu le port série et extrait les trames SENSORS:d1:d2:d3.
    Tourne en daemon thread dès qu'une connexion série est établie.
    """
    while True:
        time.sleep(0.05)
        with serial_lock:
            conn = serial_conn
        if conn is None or not conn.is_open:
            continue
        try:
            if conn.in_waiting:
                line = conn.readline().decode("utf-8", errors="replace").strip()
                if line.startswith("SENSORS:"):
                    parts = line[len("SENSORS:"):].split(":")
                    if len(parts) == 3:
                        try:
                            d1, d2, d3 = float(parts[0]), float(parts[1]), float(parts[2])
                            with sensor_lock:
                                sensor_data["s1"] = round(d1, 1)
                                sensor_data["s2"] = round(d2, 1)
                                sensor_data["s3"] = round(d3, 1)
                        except ValueError:
                            pass
        except Exception:
            pass


# Lancer le thread de lecture en arrière-plan
_reader = threading.Thread(target=_serial_reader_thread, daemon=True)
_reader.start()


# ═══════════════════════════════════════════════════
#  HELPERS SÉRIE
# ═══════════════════════════════════════════════════

def serial_connect(port: str = SERIAL_PORT) -> bool:
    global serial_conn, SERIAL_PORT
    with serial_lock:
        if serial_conn and serial_conn.is_open:
            try:
                serial_conn.close()
            except Exception:
                pass
        try:
            serial_conn = serial.Serial(port, SERIAL_BAUD, timeout=1)
            SERIAL_PORT = port
            time.sleep(2)   # Attendre le reset Arduino après ouverture du port
            print(f"[SERIAL] Connecté → {port} @ {SERIAL_BAUD} baud")
            return True
        except serial.SerialException as e:
            print(f"[SERIAL] Erreur connexion : {e}")
            serial_conn = None
            return False


def serial_send(cmd: str) -> bool:
    with serial_lock:
        if serial_conn is None or not serial_conn.is_open:
            return False
        try:
            serial_conn.write(cmd.encode())
            serial_conn.flush()
            print(f"[SERIAL] → {cmd.strip()}")
            return True
        except serial.SerialException as e:
            print(f"[SERIAL] Erreur envoi : {e}")
            return False


def serial_is_connected() -> bool:
    with serial_lock:
        return serial_conn is not None and serial_conn.is_open


def build_cmd(direction: str, value: float) -> str:
    """Construit la commande série selon le protocole de l'Arduino."""
    cmds = {
        "forward":  f"forward {value:.2f}\n",
        "backward": f"backward {value:.2f}\n",
        "left":     f"left {value:.2f}\n",
        "right":    f"right {value:.2f}\n",
        "stop":     "stop 0\n",
    }
    return cmds.get(direction, "stop 0\n")


# ═══════════════════════════════════════════════════
#  HELPERS TEXT ENGINE
# ═══════════════════════════════════════════════════

def set_language(lang: str) -> None:
    """
    Écrit config_lang.txt avant de lancer le programme C.
    Doit correspondre au format attendu par load_configuration() dans config.c.
    """
    lang = lang if lang in ("fr", "en") else "fr"
    try:
        with open(CONFIG_LANG_FILE, "w", encoding="utf-8") as f:
            f.write(f"language={lang}\n")
        print(f"[CONFIG] Langue définie → {lang}")
    except OSError as e:
        print(f"[CONFIG] Erreur écriture config_lang.txt : {e}")


def read_commands_file() -> list[str]:
    """
    Lit commands.txt généré par pfr_text.out.
    Retourne une liste de lignes ex: ["forward 2.00", "right 90.00"].
    """
    try:
        with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return []
    except OSError as e:
        print(f"[CMD FILE] Erreur lecture : {e}")
        return []


def estimate_duration(cmd_str: str) -> float:
    """
    Estime la durée d'exécution d'une commande en secondes.
    Flask attend ce délai avant d'envoyer la commande suivante,
    pour éviter de saturer l'Arduino pendant un mouvement en cours.
    Ajuste SPEED_M_PER_S et SPEED_DEG_PER_S selon ton robot.
    """
    parts = cmd_str.strip().split()
    if len(parts) < 2:
        return 0.5
    action = parts[0]
    try:
        value = float(parts[1])
    except ValueError:
        return 0.5
    if action in ("forward", "backward"):
        return (value / SPEED_M_PER_S) + 0.3
    elif action in ("left", "right"):
        return (value / SPEED_DEG_PER_S) + 0.3
    return 0.5


def run_text_engine(phrase: str, lang: str) -> dict:
    """
    Lance pfr_text.out directement sur la Pi (Linux natif, pas de WSL).

    1. Écrit config_lang.txt
    2. Supprime l'ancien commands.txt
    3. Lance pfr_text.out avec la phrase sur stdin
    4. Lit commands.txt généré

    Note : si main.c appelle commander_robot() au lieu de handle_text_request(),
    le system("python3 /home/ny_aina/...") échouera silencieusement — c'est normal,
    Flask gère l'envoi série lui-même. commands.txt sera quand même généré.
    """
    if not os.path.isfile(C_PROGRAM_PATH):
        return {
            "success": False,
            "output":  "",
            "commands": [],
            "error": (
                f"Exécutable introuvable : {C_PROGRAM_PATH}\n"
                f"Lance 'make' dans {TEXT_ENGINE_DIR}/"
            )
        }

    # 1. Langue
    set_language(lang)

    # 2. Supprimer l'ancien commands.txt
    try:
        os.remove(COMMANDS_FILE)
    except FileNotFoundError:
        pass

    # 3. Lancer le programme C
    try:
        result = subprocess.run(
            [C_PROGRAM_PATH],
            input=f"{phrase}\n",
            capture_output=True,
            text=True,
            timeout=10,
            cwd=TEXT_ENGINE_DIR,   # Répertoire de travail = TEXT_ENGINE (chemins relatifs OK)
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        output = stdout + ("\n" + stderr if stderr else "")
        print(f"[C] stdout: {stdout[:200]}")
        if stderr:
            print(f"[C] stderr: {stderr[:200]}")

        # returncode != 0 seulement si le programme crash ; une erreur "commande non reconnue"
        # retourne 0 avec c=0 dans interpret_words — on vérifie commands.txt à la place
        if result.returncode not in (0, 1):
            return {
                "success": False,
                "output":  output,
                "commands": [],
                "error": f"Crash du programme C (code {result.returncode})"
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output":  "",
            "commands": [],
            "error": "Timeout — pfr_text.out n'a pas répondu en 10 s"
        }
    except PermissionError:
        return {
            "success": False,
            "output":  "",
            "commands": [],
            "error": (
                f"Permission refusée : {C_PROGRAM_PATH}\n"
                f"Lance : chmod +x {C_PROGRAM_PATH}"
            )
        }
    except Exception as e:
        return {
            "success": False,
            "output":  "",
            "commands": [],
            "error": str(e)
        }

    # 4. Lire les commandes générées
    commands = read_commands_file()
    return {
        "success":  True,
        "output":   output,
        "commands": commands,
        "error":    None
    }


def send_commands_to_arduino(commands: list[str]) -> list[dict]:
    """
    Envoie chaque commande de commands.txt sur le port série.
    Attend la durée estimée d'exécution entre chaque commande.
    """
    results = []
    for cmd_str in commands:
        ok = serial_send(cmd_str + "\n")
        results.append({"cmd": cmd_str, "sent": ok})
        if ok:
            wait = estimate_duration(cmd_str)
            print(f"[SERIAL] Attente {wait:.1f}s…")
            time.sleep(wait)
    return results


# ═══════════════════════════════════════════════════
#  ROUTES — GÉNÉRAL
# ═══════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("robot_interface.html")


@app.route("/api/status")
def api_status():
    ports = [p.device for p in serial.tools.list_ports.comports()]
    c_ready = os.path.isfile(C_PROGRAM_PATH) and os.access(C_PROGRAM_PATH, os.X_OK)
    return jsonify({
        "serial_connected": serial_is_connected(),
        "serial_port":      SERIAL_PORT,
        "available_ports":  ports,
        "c_program_ready":  c_ready,
        "c_program_path":   C_PROGRAM_PATH,
    })


@app.route("/api/connect", methods=["POST"])
def api_connect():
    data = request.get_json(silent=True) or {}
    port = data.get("port", SERIAL_PORT)
    if serial_connect(port):
        return jsonify({"success": True, "port": port})
    return jsonify({"success": False, "error": f"Impossible d'ouvrir {port}"}), 500


@app.route("/api/disconnect", methods=["POST"])
def api_disconnect():
    global serial_conn
    with serial_lock:
        if serial_conn and serial_conn.is_open:
            serial_conn.close()
        serial_conn = None
    return jsonify({"success": True})


@app.route("/api/sensors")
def api_sensors():
    """Retourne les dernières distances lues par les capteurs ultrason."""
    with sensor_lock:
        data = dict(sensor_data)
    return jsonify(data)


# ═══════════════════════════════════════════════════
# ═══════════════════════════════════════════════════

@app.route("/api/move", methods=["POST"])
def api_move():
    """
    Envoie une commande de déplacement vers l'Arduino.

    Body JSON :
      {
        "direction": "forward" | "backward" | "left" | "right" | "stop",
        "mode":      "hold" | "timed",
        "value":     <float>   ← mètres ou degrés (ignoré en mode hold)
      }

    Mode "hold"  : press → grande valeur, release → stop 0
    Mode "timed" : valeur exacte saisie par l'utilisateur
    """
    data      = request.get_json(silent=True) or {}
    direction = data.get("direction", "stop").lower()
    mode      = data.get("mode", "hold")

    HOLD_DISTANCE_M = 50.0
    HOLD_ANGLE_DEG  = 9999.0

    if direction == "stop":
        value = 0.0
    elif mode == "hold":
        value = HOLD_ANGLE_DEG if direction in ("left", "right") else HOLD_DISTANCE_M
    else:
        value = float(data.get("value", 0.5))

    cmd = build_cmd(direction, value)
    ok  = serial_send(cmd)
    return jsonify({"success": ok, "sent": cmd.strip()})


# ═══════════════════════════════════════════════════
#  ROUTES — MODE TEXTE
# ═══════════════════════════════════════════════════

@app.route("/api/text-request", methods=["POST"])
def api_text_request():
    """
    Traite une phrase en langage naturel via pfr_text.out.

    Body JSON :
      {
        "phrase": "avance de 2 mètres puis tourne à droite",
        "lang":   "fr" | "en",
        "send":   true | false
      }

    Réponse :
      {
        "success":  bool,
        "output":   str,       ← stdout/stderr du programme C
        "commands": [{ "cmd": "forward 2.00", "sent": bool }],
        "error":    str | null
      }
    """
    data    = request.get_json(silent=True) or {}
    phrase  = data.get("phrase", "").strip()
    lang    = data.get("lang", "fr")
    do_send = data.get("send", True)

    if not phrase:
        return jsonify({"success": False, "error": "Phrase vide", "commands": []}), 400

    result = run_text_engine(phrase, lang)

    if not result["success"]:
        return jsonify(result), 500

    if do_send and result["commands"]:
        result["commands"] = send_commands_to_arduino(result["commands"])
    else:
        result["commands"] = [{"cmd": c, "sent": False} for c in result["commands"]]

    return jsonify(result)


# ═══════════════════════════════════════════════════
#  ROUTES — MODE VOCAL
# ═══════════════════════════════════════════════════

VOCAL_RESULT_FILE = os.path.join(TEXT_ENGINE_DIR, "vocal_res.txt")

@app.route("/api/vocal-request", methods=["POST"])
def api_vocal_request():
    """
    Lance l'écoute micro via Module_vocal.py (en sous-processus),
    récupère la transcription depuis vocal_res.txt,
    puis la traite comme une requête texte normale.

    Body JSON :
      {
        "lang": "fr" | "en",
        "send": true | false
      }

    Réponse :
      {
        "success":      bool,
        "transcription": str,
        "output":       str,
        "commands":     [{ "cmd": ..., "sent": bool }],
        "error":        str | null
      }
    """
    data    = request.get_json(silent=True) or {}
    lang    = data.get("lang", "fr")
    do_send = data.get("send", True)

    # 1. Supprimer l'ancien fichier de transcription
    try:
        os.remove(VOCAL_RESULT_FILE)
    except FileNotFoundError:
        pass

    # 2. Lancer Module_vocal.py
    vocal_script = os.path.join(BASE_DIR, "INTERFACE", "Module_vocal.py")
    if not os.path.isfile(vocal_script):
        # Chercher à côté de app.py
        vocal_script = os.path.join(os.path.dirname(__file__), "Module_vocal.py")

    try:
        proc = subprocess.run(
            ["python3", vocal_script],
            capture_output=True,
            text=True,
            timeout=30,          # 30s max pour parler
            cwd=TEXT_ENGINE_DIR,
        )
        print(f"[VOCAL] stdout: {proc.stdout.strip()[:200]}")
        if proc.stderr:
            print(f"[VOCAL] stderr: {proc.stderr.strip()[:200]}")
    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "transcription": "",
            "output": "",
            "commands": [],
            "error": "Timeout — aucune parole détectée en 30s"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "transcription": "",
            "output": "",
            "commands": [],
            "error": str(e)
        }), 500

    # 3. Lire la transcription depuis vocal_res.txt
    try:
        with open(VOCAL_RESULT_FILE, "r", encoding="utf-8") as f:
            transcription = f.read().strip()
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "transcription": "",
            "output": proc.stdout.strip(),
            "commands": [],
            "error": "Transcription non trouvée — parole non reconnue ?"
        }), 500

    if not transcription:
        return jsonify({
            "success": False,
            "transcription": "",
            "output": proc.stdout.strip(),
            "commands": [],
            "error": "Transcription vide"
        }), 500

    print(f"[VOCAL] Transcription : {transcription}")

    # 4. Traiter la transcription comme une requête texte
    result = run_text_engine(transcription, lang)
    result["transcription"] = transcription

    if not result["success"]:
        return jsonify(result), 500

    if do_send and result["commands"]:
        result["commands"] = send_commands_to_arduino(result["commands"])
    else:
        result["commands"] = [{"cmd": c, "sent": False} for c in result["commands"]]

    return jsonify(result)


# ═══════════════════════════════════════════════════
#  ROUTES — SLAM LIDAR
# ═══════════════════════════════════════════════════

SLAM_START_SCRIPT = "/home/groupe5/start_slam.sh"
SLAM_SAVE_SCRIPT  = "/home/groupe5/save_map.sh"
SLAM_STOP_SCRIPT  = "/home/groupe5/stop_slam.sh"

@app.route("/api/slam/start", methods=["POST"])
def api_slam_start():
    """Lance le script start_slam.sh en arrière-plan."""
    if not os.path.isfile(SLAM_START_SCRIPT):
        return jsonify({"success": False, "error": f"Script introuvable : {SLAM_START_SCRIPT}"}), 404
    try:
        subprocess.Popen(
            ["bash", SLAM_START_SCRIPT],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/slam/save", methods=["POST"])
def api_slam_save():
    """Lance le script save_map.sh et attend sa fin."""
    if not os.path.isfile(SLAM_SAVE_SCRIPT):
        return jsonify({"success": False, "error": f"Script introuvable : {SLAM_SAVE_SCRIPT}"}), 404
    try:
        result = subprocess.run(
            ["bash", SLAM_SAVE_SCRIPT],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return jsonify({"success": True, "output": result.stdout.strip()})
        return jsonify({"success": False, "error": result.stderr.strip() or "Erreur inconnue"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Timeout — carte non sauvegardée"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/slam/stop", methods=["POST"])
def api_slam_stop():
    """Lance le script stop_slam.sh et attend sa fin."""
    if not os.path.isfile(SLAM_STOP_SCRIPT):
        return jsonify({"success": False, "error": f"Script introuvable : {SLAM_STOP_SCRIPT}"}), 404
    try:
        result = subprocess.run(
            ["bash", SLAM_STOP_SCRIPT],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0:
            return jsonify({"success": True, "output": result.stdout.strip()})
        return jsonify({"success": False, "error": result.stderr.strip() or "Erreur inconnue"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Timeout — arrêt échoué"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═══════════════════════════════════════════════════
#  ROUTE — CARTE LIDAR
# ═══════════════════════════════════════════════════

def _pgm_to_png_bytes(path: str) -> bytes:
    """
    Lit un fichier PGM (P5 binaire ou P2 ASCII) et retourne un PNG en mémoire.
    Dépendance zéro : utilise uniquement la stdlib Python (struct + zlib).
    """
    with open(path, "rb") as f:
        raw = f.read()

    lines = raw.split(b"\n")
    idx = 0

    # Sauter les commentaires
    header = []
    while len(header) < 3:
        line = lines[idx].strip()
        idx += 1
        if line.startswith(b"#") or not line:
            continue
        # Une ligne peut contenir plusieurs tokens
        header.extend(line.split())

    magic  = header[0].decode()
    width  = int(header[1])
    height = int(header[2])
    maxval = int(header[3]) if len(header) > 3 else 255

    if magic == "P5":
        # binaire : les pixels viennent après le 3e saut de ligne
        offset = 0
        count  = 0
        for i, b in enumerate(raw):
            if b == ord("\n"):
                count += 1
                if count == 3:
                    offset = i + 1
                    break
        pixels = raw[offset:offset + width * height]
    elif magic == "P2":
        vals   = b" ".join(lines[idx:]).split()
        pixels = bytes([int(v) for v in vals])
    else:
        raise ValueError(f"Format PGM non supporté : {magic}")

    # Normaliser si maxval != 255
    if maxval != 255:
        pixels = bytes([int(p * 255 / maxval) for p in pixels])

    # Construire le PNG minimal (RGB 8 bits, pas d'entrelacement)
    def make_chunk(ctype: bytes, data: bytes) -> bytes:
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = make_chunk(b"IHDR", ihdr_data)

    # IDAT — chaque ligne précédée du filtre 0
    raw_rows = b""
    for y in range(height):
        row = pixels[y * width:(y + 1) * width]
        # Grayscale → RGB
        rgb_row = bytearray(width * 3)
        for x in range(width):
            v = row[x]
            rgb_row[x * 3]     = v
            rgb_row[x * 3 + 1] = v
            rgb_row[x * 3 + 2] = v
        raw_rows += b"\x00" + bytes(rgb_row)

    compressed = zlib.compress(raw_rows, 9)
    idat = make_chunk(b"IDAT", compressed)
    iend = make_chunk(b"IEND", b"")

    signature = b"\x89PNG\r\n\x1a\n"
    return signature + ihdr + idat + iend


@app.route("/api/map")
def api_map():
    """
    Sert la carte LiDAR (ma_carte.pgm) convertie à la volée en PNG.
    Paramètre optionnel : ?t=<timestamp> (cache-busting ignoré côté serveur).
    """
    if not os.path.isfile(MAP_FILE):
        return jsonify({
            "error": f"Carte introuvable : {MAP_FILE}",
            "hint":  "Lance le nœud de cartographie ROS 2 puis sauvegarde la carte avec map_saver_cli."
        }), 404
    try:
        png = _pgm_to_png_bytes(MAP_FILE)
        return Response(png, mimetype="image/png",
                        headers={"Cache-Control": "no-store"})
    except Exception as e:
        return jsonify({"error": f"Erreur lecture carte : {e}"}), 500


@app.route("/api/map/info")
def api_map_info():
    """Retourne les métadonnées de la carte (taille, date de modification)."""
    if not os.path.isfile(MAP_FILE):
        return jsonify({"available": False}), 404
    stat = os.stat(MAP_FILE)
    return jsonify({
        "available": True,
        "size_bytes": stat.st_size,
        "mtime": stat.st_mtime,
        "path": MAP_FILE,
    })


# ═══════════════════════════════════════════════════
#  POINT D'ENTRÉE
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 58)
    print("  Interface Robot — Raspberry Pi 3B")
    print(f"  Port série    : {SERIAL_PORT}  |  Baud : {SERIAL_BAUD}")
    print(f"  Moteur C      : {C_PROGRAM_PATH}")
    print(f"  commands.txt  : {COMMANDS_FILE}")
    print("  URL           : http://<IP_du_Pi>:5000")
    print("=" * 58)

    # Vérifications au démarrage
    if not os.path.isfile(C_PROGRAM_PATH):
        print(f"⚠  ATTENTION : {C_PROGRAM_PATH} introuvable → lance 'make' dans TEXT_ENGINE/")
    elif not os.access(C_PROGRAM_PATH, os.X_OK):
        print(f"⚠  ATTENTION : {C_PROGRAM_PATH} non exécutable → lance 'chmod +x {C_PROGRAM_PATH}'")
    else:
        print(f"✓  pfr_text.out trouvé et exécutable")

    serial_connect(SERIAL_PORT)

    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)