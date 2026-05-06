"""
Serveur Flask — Interface Web Robot (Raspberry Pi 3B)
-----------------------------------------------------
Communication série USB avec l'Arduino (115200 baud).

Protocole série (robot_arduino_improved.ino) :
  "forward <metres>\\n"   → avancer
  "backward <metres>\\n"  → reculer
  "right <degrees>\\n"    → tourner à droite
  "left <degrees>\\n"     → tourner à gauche
  "stop 0\\n"             → arrêt immédiat

Moteur de requêtes texte (TEXT_ENGINE) :
  Le programme C (pfr_text.out) lit UNE phrase sur stdin et exporte les
  commandes dans commands.txt (même format que le protocole série).
  Le backend lit ce fichier et envoie les commandes à l'Arduino.

Structure attendue :
  Windows :  D:\\PFR\\PFR_G5_Upssitech\\PFR2\\INTERFACE\\
  ├── app.py                  ← ce fichier
  └── templates/
      └── index.html

  WSL (Linux) : /mnt/d/PFR/PFR_G5_Upssitech/PFR2/TEXT_ENGINE/
  ├── pfr_text.out        ← exécutable compilé (make)
  ├── lexique_fr.txt
  ├── lexique_en.txt
  ├── config_lang.txt
  └── commands.txt        ← généré par le programme C (même fichier vu des deux côtés)

Lancement : python app.py  (depuis Windows, PowerShell ou CMD)
"""

import os
import subprocess
import threading
import time

import serial
import serial.tools.list_ports
from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════════════════
#  CONFIGURATION SÉRIE
# ═══════════════════════════════════════════════════

SERIAL_PORT = os.environ.get("ROBOT_PORT", "/dev/ttyUSB0")
SERIAL_BAUD = 115200

# ═══════════════════════════════════════════════════
#  CONFIGURATION TEXT ENGINE (WSL)
# ═══════════════════════════════════════════════════

# Chemin Linux (WSL) vers le dossier TEXT_ENGINE de PFR2
WSL_TEXT_ENGINE_DIR = "/mnt/d/PFR/PFR_G5_Upssitech/PFR2/TEXT_ENGINE"

# Exécutable compilé côté WSL
WSL_C_PROGRAM_PATH = f"{WSL_TEXT_ENGINE_DIR}/pfr_text.out"

# config_lang.txt — accessible depuis Windows ET WSL (même fichier physique)
WSL_CONFIG_LANG_FILE = f"{WSL_TEXT_ENGINE_DIR}/config_lang.txt"
WIN_CONFIG_LANG_FILE = r"D:\PFR\PFR_G5_Upssitech\PFR2\TEXT_ENGINE\config_lang.txt"

# commands.txt — écrit par le programme C dans TEXT_ENGINE, lisible depuis Windows ET WSL
WSL_COMMANDS_FILE = f"{WSL_TEXT_ENGINE_DIR}/commands.txt"
WIN_COMMANDS_FILE = r"D:\PFR\PFR_G5_Upssitech\PFR2\TEXT_ENGINE\commands.txt"

# Délai entre deux commandes série envoyées en séquence (secondes)
INTER_CMD_DELAY = 0.05

# Seuil d'alerte obstacle capteur ultrason (cm)
OBSTACLE_THRESHOLD_CM = 20

# ═══════════════════════════════════════════════════
#  ÉTAT GLOBAL
# ═══════════════════════════════════════════════════

serial_conn: serial.Serial | None = None
serial_lock = threading.Lock()


# ═══════════════════════════════════════════════════
#  HELPERS SÉRIE
# ═══════════════════════════════════════════════════

def serial_connect(port: str = SERIAL_PORT) -> bool:
    """Ouvre la connexion série avec l'Arduino."""
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
            time.sleep(2)          # Attendre le reset Arduino
            print(f"[SERIAL] Connecté → {port} @ {SERIAL_BAUD} baud")
            return True
        except serial.SerialException as e:
            print(f"[SERIAL] Erreur connexion : {e}")
            serial_conn = None
            return False


def serial_send(cmd: str) -> bool:
    """Envoie une commande brute sur le port série."""
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
    """Construit la commande série à envoyer à l'Arduino."""
    cmds = {
        "forward":  f"forward {value:.2f}\n",
        "backward": f"backward {value:.2f}\n",
        "left":     f"left {value:.2f}\n",
        "right":    f"right {value:.2f}\n",
        "stop":     "stop 0\n",
    }
    return cmds.get(direction, "stop 0\n")


# ═══════════════════════════════════════════════════
#  HELPERS TEXT ENGINE (via WSL)
# ═══════════════════════════════════════════════════

def wsl_file_exists(wsl_path: str) -> bool:
    """Vérifie qu'un fichier existe dans WSL sans passer par os.path."""
    try:
        check = subprocess.run(
            ["wsl.exe", "-e", "bash", "-c", f"test -f '{wsl_path}' && echo ok"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return check.stdout.strip() == "ok"
    except Exception:
        return False


def set_language(lang: str) -> None:
    """
    Écrit la langue dans config_lang.txt.
    lang : "fr" (langue=1) ou "en" (langue=2)
    Le fichier est dans TEXT_ENGINE, accessible depuis Windows et WSL.
    """
    lang = lang if lang in ("fr", "en") else "fr"
    try:
        with open(WIN_CONFIG_LANG_FILE, "w", encoding="utf-8") as f:
            f.write(f"language={lang}\n")
    except OSError as e:
        print(f"[CONFIG] Impossible d'écrire config_lang.txt : {e}")


def delete_old_commands() -> None:
    """Supprime l'ancien commands.txt pour éviter les résidus."""
    # Via Windows (accès direct au fichier partagé)
    try:
        os.remove(WIN_COMMANDS_FILE)
    except FileNotFoundError:
        pass
    except OSError as e:
        print(f"[CMD FILE] Impossible de supprimer : {e}")


def read_commands_file() -> list[str]:
    """
    Lit commands.txt généré par le programme C.
    Le fichier est dans TEXT_ENGINE — accessible directement depuis Windows.
    Retourne une liste de lignes valides ex: ["forward 2.00", "right 90.00"].
    """
    # Lecture directe via Windows (chemin partagé avec WSL)
    if os.path.isfile(WIN_COMMANDS_FILE):
        try:
            with open(WIN_COMMANDS_FILE, "r", encoding="utf-8") as f:
                return [l.strip() for l in f if l.strip()]
        except OSError as e:
            print(f"[CMD FILE] Erreur lecture : {e}")

    # Fallback via WSL
    try:
        result = subprocess.run(
            ["wsl.exe", "-e", "bash", "-c", f"cat '{WSL_COMMANDS_FILE}' 2>/dev/null"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
        )
        if result.stdout.strip():
            return [l.strip() for l in result.stdout.splitlines() if l.strip()]
    except Exception as e:
        print(f"[CMD FILE] Erreur lecture WSL : {e}")

    return []


def run_text_engine(phrase: str, lang: str) -> dict:
    """
    Lance pfr_text.out (via WSL) pour traiter une phrase en langage naturel.

    Retourne :
    {
        "success":  bool,
        "output":   str,       # stdout du programme C
        "commands": [str],     # lignes de commands.txt
        "error":    str | None
    }
    """
    # 1. Vérifier que l'exécutable existe dans WSL
    if not wsl_file_exists(WSL_C_PROGRAM_PATH):
        return {
            "success": False,
            "output":  "",
            "commands": [],
            "error": (
                f"Exécutable introuvable dans WSL : {WSL_C_PROGRAM_PATH}\n"
                f"Lancez 'make' dans le dossier text_engine/ sous WSL."
            )
        }

    # 2. Langue
    set_language(lang)

    # 3. Supprimer l'ancien commands.txt
    delete_old_commands()

    # 4. Lancer le programme C via WSL
    bash_cmd = f"cd '{WSL_TEXT_ENGINE_DIR}' && '{WSL_C_PROGRAM_PATH}'"
    try:
        result = subprocess.run(
            ["wsl.exe", "-e", "bash", "-c", bash_cmd],
            input=f"{phrase}\n",
            capture_output=True,
            text=True,
            timeout=10,
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        output = stdout + ("\n" + stderr if stderr else "")

        if result.returncode != 0:
            return {
                "success": False,
                "output":  output,
                "commands": [],
                "error": f"Le programme s'est terminé avec le code {result.returncode}"
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output":  "",
            "commands": [],
            "error": "Timeout — le programme C n'a pas répondu en 10 s"
        }
    except Exception as e:
        return {
            "success": False,
            "output":  "",
            "commands": [],
            "error": str(e)
        }

    # 5. Lire les commandes générées
    commands = read_commands_file()

    return {
        "success":  True,
        "output":   output,
        "commands": commands,
        "error":    None
    }


def estimate_duration(cmd_str: str) -> float:
    """Estime la durée d'exécution d'une commande en secondes."""
    parts = cmd_str.strip().split()
    if len(parts) < 2:
        return 0.5
    action = parts[0]
    try:
        value = float(parts[1])
    except ValueError:
        return 0.5

    # ⚠️ Ajustez ces vitesses selon votre robot
    SPEED_M_PER_S  = 0.4   # vitesse en ligne droite (m/s)
    SPEED_DEG_PER_S = 180.0  # vitesse de rotation (degrés/s)

    if action in ("forward", "backward"):
        return (value / SPEED_M_PER_S) + 0.3   # +0.3s de marge
    elif action in ("left", "right"):
        return (value / SPEED_DEG_PER_S) + 0.3
    return 0.5

def send_commands_to_arduino(commands: list[str]) -> list[dict]:
    results = []
    for cmd_str in commands:
        ok = serial_send(cmd_str + "\n")
        results.append({"cmd": cmd_str, "sent": ok})
        if ok:
            wait = estimate_duration(cmd_str)
            print(f"[SERIAL] Attente {wait:.1f}s avant prochaine commande...")
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
    return jsonify({
        "serial_connected": serial_is_connected(),
        "serial_port":      SERIAL_PORT,
        "available_ports":  ports,
        "c_program_ready":  wsl_file_exists(WSL_C_PROGRAM_PATH),
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


# ═══════════════════════════════════════════════════
#  ROUTES — MODE MANUEL
# ═══════════════════════════════════════════════════

@app.route("/api/move", methods=["POST"])
def api_move():
    """
    Envoie une commande de déplacement vers l'Arduino.

    Body JSON :
      {
        "direction": "forward" | "backward" | "left" | "right" | "stop",
        "mode":      "hold" | "timed",
        "value":     <float>   ← mètres (forward/backward) ou degrés (left/right)
      }

    Mode "hold"  : bouton pressé → grande valeur, relâché → stop.
    Mode "timed" : valeur exacte fournie par l'utilisateur.
    """
    data      = request.get_json(silent=True) or {}
    direction = data.get("direction", "stop").lower()
    mode      = data.get("mode", "hold")

    # Valeurs larges pour le mode "hold" (l'Arduino s'arrête sur "stop")
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
    Traite une phrase en langage naturel via le moteur C (WSL).

    Body JSON :
      {
        "phrase": "avance de 2 mètres puis tourne à droite",
        "lang":   "fr" | "en",
        "send":   true | false   ← envoyer les commandes à l'Arduino ?
      }

    Réponse :
      {
        "success":  bool,
        "output":   str,           ← stdout du programme C
        "commands": [              ← commandes générées
          { "cmd": "forward 2.00", "sent": true }
        ],
        "error":    str | null
      }
    """
    data    = request.get_json(silent=True) or {}
    phrase  = data.get("phrase", "").strip()
    lang    = data.get("lang", "fr")
    do_send = data.get("send", True)

    if not phrase:
        return jsonify({"success": False, "error": "Phrase vide", "commands": []}), 400

    # Lancer le moteur C via WSL
    result = run_text_engine(phrase, lang)

    if not result["success"]:
        return jsonify(result), 500

    # Envoyer à l'Arduino si demandé
    if do_send and result["commands"]:
        result["commands"] = send_commands_to_arduino(result["commands"])
    else:
        result["commands"] = [{"cmd": c, "sent": False} for c in result["commands"]]

    return jsonify(result)


# ═══════════════════════════════════════════════════
#  POINT D'ENTRÉE
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  Interface Robot — Serveur Flask")
    print(f"  Port série      : {SERIAL_PORT}  |  Baud : {SERIAL_BAUD}")
    print(f"  Moteur C (WSL)  : {WSL_C_PROGRAM_PATH}")
    print(f"  commands.txt    : {WIN_COMMANDS_FILE}")
    print(f"  Config langue   : {WIN_CONFIG_LANG_FILE}")
    print("  URL             : http://localhost:5000")
    print("=" * 60)

    # Tentative de connexion automatique au démarrage
    serial_connect(SERIAL_PORT)

    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)