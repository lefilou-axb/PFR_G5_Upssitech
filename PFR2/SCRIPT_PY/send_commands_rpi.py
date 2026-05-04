#!/usr/bin/env python3
"""
Script pour la Raspberry Pi 3A+
Envoie les commandes du fichier commands.txt à l'Arduino Mega
"""

import serial
import time
import sys
from pathlib import Path

# Configuration
ARDUINO_PORT = 'COM3'  # À adapter si différent (ttyUSB0, ttyUSB1, etc.)
BAUD_RATE = 115200
COMMANDS_FILE = 'commands.txt'  # Chemin du fichier de commandes

def find_arduino_port():
    """Cherche le port Arduino automatiquement"""
    import glob
    
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    
    if not ports:
        print("Aucun port Arduino trouvé!")
        return None
    
    print(f"Ports trouvés: {ports}")
    if len(ports) == 1:
        return ports[0]
    
    print("Sélectionner le port Arduino:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port}")
    
    choice = input("Entrez le numéro: ")
    return ports[int(choice) - 1]

def send_commands(file_path, port, baud_rate):
    """Envoie les commandes du fichier à l'Arduino"""
    
    # Vérifier si le fichier existe
    if not Path(file_path).exists():
        print(f"Fichier '{file_path}' non trouvé!")
        return False
    
    # Connexion à l'Arduino
    try:
        print(f"Connexion à {port} ({baud_rate} baud)...")
        ser = serial.Serial(port, baud_rate, timeout=2)
        time.sleep(2)  # Attendre l'initialisation
        print("Connecté à l'Arduino\n")
    except serial.SerialException as e:
        print(f"Impossible de se connecter: {e}")
        return False
    
    try:
        # Lire et envoyer les commandes
        with open(file_path, 'r') as f:
            commands = [line.strip() for line in f if line.strip()]
        
        print(f"{len(commands)} commande(s) à envoyer:\n")
        for i, cmd in enumerate(commands, 1):
            print(f"  {i}. {cmd}")
        print("\n" + "="*50 + "\n")
        
        # Envoyer chaque commande
        for i, cmd in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] Envoi: {cmd}")
            
            # Envoyer la commande
            ser.write((cmd + '\n').encode())
            
            # Attendre que l'Arduino execute
            # (adapter le délai selon la commande)
            if 'forward' in cmd.lower() or 'backward' in cmd.lower():
                delay = float(cmd.split()[-1]) * 3  # Adapter ce délai
            elif 'right' in cmd.lower() or 'left' in cmd.lower():
                delay = float(cmd.split()[-1]) * 0.01  # Adapter ce délai
            else:
                delay = 1
            
            time.sleep(delay + 0.5)  # Pause entre les commandes
            
            # Lire les réponses de l'Arduino
            print("  Arduino dit:")
            while ser.in_waiting > 0:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    print(f"    {response}")
        
        print("\n" + "="*50)
        print("Toutes les commandes ont été envoyées!")
        
    except KeyboardInterrupt:
        print("\nInterruption par l'utilisateur")
    except Exception as e:
        print(f"Erreur: {e}")
        return False
    finally:
        ser.close()
        print("Déconnecté")
    
    return True

def main():
    """Fonction principale"""
    print("\n╔════════════════════════════════════════╗")
    print("║  Gestionnaire de Commandes pour Robot  ║")
    print("║     (Raspberry Pi → Arduino Mega)      ║")
    print("╚════════════════════════════════════════╝\n")
    
    # Chercher le port si non spécifié
    port = ARDUINO_PORT
    if not any(p in port for p in ['ttyUSB', 'ttyACM', 'COM']):
        port = find_arduino_port()
        if not port:
            return
    
    # Vérifier si c'est le bon fichier
    if not Path(COMMANDS_FILE).exists():
        print(f"Fichier '{COMMANDS_FILE}' non trouvé")
        file_input = input("Entrez le chemin du fichier: ").strip()
        if file_input:
            commands_file = file_input
        else:
            print("Aucun fichier spécifié")
            return
    else:
        commands_file = COMMANDS_FILE
    
    # Envoyer les commandes
    send_commands(commands_file, port, BAUD_RATE)

if __name__ == '__main__':
    main()
