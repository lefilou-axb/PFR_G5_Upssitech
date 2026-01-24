import csv
import turtle as t

def readFile():
    with open("C:/Users/lucas/OneDrive/Documents/etudes/Upssitech/PFR/Simulation/commandes.txt", "r", encoding="utf-8") as fichier:
        for ligne in fichier:
            ligne = ligne.strip()  # enlève \n et espaces

            if not ligne:
                continue  # ignore lignes vides
            
            
            instruction = ligne.split()
            
            commande = instruction[0]

            if len(instruction[1]) > 1:
                try :
                    valeur = float(instruction[1])
                except ValueError:
                        print(f"Valeur invalide : '{instruction[1]}'")
                        continue
            else:
                valeur = 1
        
            if commande == "avance":
                t.forward(valeur)
            elif commande == "tourne":
                t.left(valeur)
            else:
                print(f"Commande inconnue : {commande}")
            print(f"Commande : {commande}")


readFile()