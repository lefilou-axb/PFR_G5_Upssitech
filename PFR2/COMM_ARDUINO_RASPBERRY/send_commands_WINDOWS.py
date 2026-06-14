#!/usr/bin/env python3

import serial
import time
from pathlib import Path

# ==================== CONFIGURATION ====================
ARDUINO_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
COMMANDS_FILE = '/home/ny_aina/commands.txt'

# ==================== FONCTIONS ====================

def trouver_port_arduino():
    import serial.tools.list_ports
    ports = [port.device for port in serial.tools.list_ports.comports()]

    if not ports:
        print("❌ Aucun port COM trouvé!")
        return None

    print(f"🔌 Ports détectés: {ports}")

    if len(ports) == 1:
        return ports[0]

    print("\nSélectionner le port Arduino:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port}")

    try:
        choice = int(input("\nEntrez le numéro: "))
        return ports[choice - 1]
    except (ValueError, IndexError):
        print("❌ Choix invalide")
        return None

def envoyer_commandes(file_path, port, baud_rate):
    if not Path(file_path).exists():
        print(f"❌ Fichier '{file_path}' non trouvé!")
        return False

    try:
        print(f"\n🔗 Connexion à {port} ({baud_rate} baud)...")
        ser = serial.Serial(port, baud_rate, timeout=2)
        time.sleep(2)
        print("✅ Connecté à l'Arduino\n")
    except serial.SerialException as e:
        print(f"❌ Impossible de se connecter: {e}")
        return False

    try:
        with open(file_path, 'r') as f:
            commands = [line.strip() for line in f if line.strip()]

        if not commands:
            print("⚠️  Fichier vide!")
            return False

        print(f"📋 {len(commands)} commande(s) à envoyer:\n")
        for i, cmd in enumerate(commands, 1):
            print(f"  {i}. {cmd}")
        print("\n" + "="*60 + "\n")

        for i, cmd in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] 📤 Envoi: {cmd}")
            ser.write((cmd + '\n').encode())

            try:
                parts = cmd.split()
                cmd_type = parts[0].lower()
                value = float(parts[-1]) if len(parts) > 1 else 0

                if 'forward' in cmd_type or 'backward' in cmd_type or 'avance' in cmd_type or 'recule' in cmd_type:
                    delay = value * 5.0 + 1.0
                elif 'right' in cmd_type or 'left' in cmd_type or 'droite' in cmd_type or 'gauche' in cmd_type:
                    delay = (value / 90.0) * 0.75 + 0.5
                else:
                    delay = 0.5
            except:
                delay = 1.0

            time.sleep(delay)

            print("  📥 Arduino dit:")
            response_count = 0
            while ser.in_waiting > 0 and response_count < 10:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    print(f"     > {response}")
                    response_count += 1
                time.sleep(0.1)

            if response_count == 0:
                print("     > (pas de réponse)")

        print("\n" + "="*60)
        print("✅ Toutes les commandes ont été envoyées!")

    except KeyboardInterrupt:
        print("\n\n⛔ Interruption par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        ser.close()
        print("🔌 Déconnecté\n")

    return True

def main():
    print("\n" + "="*60)
    print("  Gestionnaire de Commandes pour Robot Arduino")
    print("="*60 + "\n")

    port = ARDUINO_PORT

    if not (port.startswith('COM') or port.startswith('/dev/')):
        print(f"⚠️  Port spécifié '{port}' invalide")
        port = trouver_port_arduino()
        if not port:
            return

    print(f"Port utilisé: {port}")

    commands_file = COMMANDS_FILE
    if not Path(commands_file).exists():
        print(f"\n⚠️  Fichier '{commands_file}' non trouvé")
        file_input = input("Entrez le chemin du fichier: ").strip()
        if file_input and Path(file_input).exists():
            commands_file = file_input
        else:
            print("❌ Fichier invalide")
            return

    print(f"Fichier: {commands_file}\n")
    envoyer_commandes(commands_file, port, BAUD_RATE)

if __name__ == '__main__':
    main()