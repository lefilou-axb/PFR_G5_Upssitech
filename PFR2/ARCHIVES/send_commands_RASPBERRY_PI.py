#!/usr/bin/env python3
"""
SCRIPT RASPBERRY PI
Envoie les commandes du fichier commands.txt à l'Arduino Mega via USB
"""

import serial
import time
import sys
import glob
from pathlib import Path

# ==================== CONFIGURATION ====================
# Sur Raspberry Pi, le port est généralement /dev/ttyUSB0 ou /dev/ttyACM0
ARDUINO_PORT = '/dev/ttyUSB0'  # À adapter si /dev/ttyUSB1 ou /dev/ttyACM0
BAUD_RATE = 115200
COMMANDS_FILE = 'commands.txt'

# ==================== FONCTIONS ====================

def trouver_port_arduino():
    """Cherche automatiquement le port Arduino sur Raspberry"""
    
    # Sur RPi, les ports USB/ACM sont dans /dev/
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    
    if not ports:
        print(" Aucun port Arduino trouvé!")
        print("\nTroubleshooting:")
        print("  1. Vérifier que l'Arduino est branché en USB")
        print("  2. Exécuter: lsusb")
        print("  3. Exécuter: ls /dev/ttyUSB*")
        return None
    
    print(f" Ports Arduino détectés: {ports}")
    
    if len(ports) == 1:
        print(f" Port unique trouvé: {ports[0]}")
        return ports[0]
    
    # Plusieurs ports détectés
    print("\nSélectionner le port Arduino:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port}")
    
    try:
        choice = int(input("\nEntrez le numéro: "))
        return ports[choice - 1]
    except (ValueError, IndexError):
        print(" Choix invalide")
        return None

def envoyer_commandes(file_path, port, baud_rate):
    """Envoie les commandes du fichier à l'Arduino"""
    
    # Vérifier si le fichier existe
    if not Path(file_path).exists():
        print(f" Fichier '{file_path}' non trouvé!")
        print(f"   Endroit cherché: {Path(file_path).absolute()}")
        return False
    
    # Connexion à l'Arduino
    try:
        print(f"\n Connexion à {port} ({baud_rate} baud)...")
        ser = serial.Serial(port, baud_rate, timeout=2)
        time.sleep(2)  # Attendre l'initialisation de l'Arduino
        print(" Connecté à l'Arduino\n")
    except serial.SerialException as e:
        print(f" Impossible de se connecter à {port}")
        print(f"   Erreur: {e}")
        print("\nSolutions:")
        print("  1. Vérifier les permissions: sudo usermod -a -G dialout $USER")
        print("  2. Redémarrer la Raspberry")
        print("  3. Vérifier que l'Arduino est bien branché")
        return False
    
    try:
        # Lire les commandes
        with open(file_path, 'r') as f:
            commands = [line.strip() for line in f if line.strip()]
        
        if not commands:
            print(f"  Fichier vide!")
            return False
        
        print(f" {len(commands)} commande(s) à envoyer:\n")
        for i, cmd in enumerate(commands, 1):
            print(f"  {i}. {cmd}")
        print("\n" + "="*60 + "\n")
        
        # Envoyer chaque commande
        for i, cmd in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}]  Envoi: {cmd}")
            
            # Envoyer la commande (ajouter newline)
            ser.write((cmd + '\n').encode())
            
            # Calculer le délai d'attente (adapter avec vos valeurs de calibrage)
            try:
                parts = cmd.split()
                cmd_type = parts[0].lower()
                value = float(parts[-1]) if len(parts) > 1 else 0
                
                # Délais basés sur le calibrage
                # À ADAPTER selon vos mesures!
                if 'forward' in cmd_type or 'avance' in cmd_type:
                    # Exemple: 1m en 5 secondes
                    delay = value * 5.0 + 1.0
                elif 'backward' in cmd_type or 'recule' in cmd_type:
                    # Même que forward
                    delay = value * 5.0 + 1.0
                elif 'right' in cmd_type or 'droite' in cmd_type:
                    # Exemple: 90° en 750ms
                    delay = (value / 90.0) * 0.75 + 0.5
                elif 'left' in cmd_type or 'gauche' in cmd_type:
                    # Même que right
                    delay = (value / 90.0) * 0.75 + 0.5
                else:
                    delay = 0.5
                    
            except:
                delay = 1.0
            
            print(f"    Attente: {delay:.1f}s")
            time.sleep(delay)
            
            # Lire les réponses de l'Arduino
            print("   Réponses Arduino:")
            response_count = 0
            start_time = time.time()
            
            while time.time() - start_time < 1.0 and response_count < 10:
                if ser.in_waiting > 0:
                    try:
                        response = ser.readline().decode('utf-8', errors='ignore').strip()
                        if response:
                            print(f"     > {response}")
                            response_count += 1
                    except:
                        pass
                time.sleep(0.05)
            
            if response_count == 0:
                print(f"     > (pas de réponse)")
        
        print("\n" + "="*60)
        print(" Toutes les commandes ont été envoyées avec succès!")
        
    except KeyboardInterrupt:
        print("\n\n Interruption par l'utilisateur")
    except Exception as e:
        print(f" Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            ser.close()
            print(" Déconnecté\n")
        except:
            pass
    
    return True

def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("  Gestionnaire de Commandes pour Robot Arduino")
    print("  (Raspberry Pi 3A+ → Arduino Mega)")
    print("="*60 + "\n")
    
    # Chercher le port automatiquement
    port = ARDUINO_PORT
    
    # Vérifier si c'est un port valide
    if not Path(port).exists():
        print(f"  Port par défaut '{port}' non détecté")
        port = trouver_port_arduino()
        if not port:
            return
    else:
        print(f" Port détecté: {port}\n")
    
    # Vérifier le fichier
    commands_file = COMMANDS_FILE
    if not Path(commands_file).exists():
        print(f"\n  Fichier '{commands_file}' non trouvé dans le dossier courant")
        file_input = input("Entrez le chemin du fichier: ").strip()
        if file_input and Path(file_input).exists():
            commands_file = file_input
        else:
            print(" Fichier invalide")
            return
    
    print(f"Fichier: {Path(commands_file).absolute()}\n")
    
    # Envoyer les commandes
    envoyer_commandes(commands_file, port, BAUD_RATE)

if __name__ == '__main__':
    main()
