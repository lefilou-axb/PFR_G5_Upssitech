"""
Serveur Flask — Interface Web Robot (Raspberry Pi 3B)
=====================================================
À placer dans : /home/groupe5/Documents/PFR/INTERFACE/app.py

Structure attendue sur la Pi :
  /home/groupe5/Documents/PFR/
  ├── INTERFACE/
  │   ├── app.py              ← ce fichier
  │   └── templates/
  │       └── index.html
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

import os
import subprocess
import threading
import time

import serial
import serial.tools.list_ports
from flask import Flask, jsonify, render_template, request
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
    return render_template("index.html")


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
