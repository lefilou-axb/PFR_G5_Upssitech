# ***************************************************************************************
#   Nom : Haegel                                                                        *
#   Prénom : Lucas                                                                      *
#   Définition : Ce fichier contient le programme permettant le déplacement du robot    *
#           dans une interface visible. Il implémente les caractéristiques de           *
#           l'environnement et des obstacles ainsi la lecture et l'exécutions des       *
#           commandes de déplacement à exécuter                                         *
#                                                                                       *
# ***************************************************************************************

#Bibiliothèques
import turtle as t
import table
import os

#PATH
Dossier_simulation = os.path.dirname(os.path.abspath(__file__))

Commmandes = os.path.join(Dossier_simulation, "..", "commands.txt")


piece = table.lecturePiece(os.path.join(Dossier_simulation, "Piece_5.txt"))
#print(f"Piece chargée : {piece}")

#Piece par defaut
if piece is None:
    print("Aucune pièce trouvée, pièce par défaut chargée")
    piece = {
        "nom"                  : "defaut",
        "dimensions"           : (400, 400),
        "positionCoinHautDroit": (200, 200),
        "obstacle"             : []
    }

#Chargement des objets
#piece["obstacle"] = table.chargerObjet(Dossier_simulation)

# Initialisation de la liste qui va contenir les commandes du fichier
cmd_list = []
depart = (50,50)

# Lecture du fichier et remplissage de la liste des commandes
with open("C:/Users/lucas/OneDrive/Documents/etudes/Upssitech/PFR/PFR_G5_Upssitech/Rattrapage/IHM/commands.txt","r") as file:
    for ligne in file:
        ligne = ligne.strip()
        #print(ligne)
        cmd_list.append(ligne)
#print(cmd_list)

table.tracerPiece(piece)
t.goto(depart)

while True:
    # Déplacement du robot et choix du mode
    #Initialisation des déplacements
    #t.goto(depart) #Fais revenir le robot à sa position de départ
    t.width(2)
    t.up()

    print("Mode de déplacement :")
    print("1 - Fichier de commandes")
    print("2 - Mode automatique")
    print("3 - Quitter")
    mode = input("Choix : ")

    if mode == "1": 
        t.color('red')
        t.down()
        t.speed(1)

        for i in range(len(cmd_list)):
            valeur = 0
            try :
                instruction = cmd_list[i].split()
            except :
                print("Commmande inconnue\n")

            commande = instruction[0]
            try :
                valeur = float(instruction[1])
            except :
                print(f"Pas de valeur pour la commande : {commande}")
            
            # Tests pour effectuer les déplacements
            if(commande == "forward"):
                distance_totale = int(valeur * 100)
                pas = 10
                for _ in range(0, distance_totale, pas):
                    if not table.detection_mur(t.xcor(), t.ycor(), t.heading(), piece) and not table.obstacle_devant(t.xcor(), t.ycor(), t.heading(), piece["obstacle"]):
                        t.forward(pas)
                    else:
                        print("Déplacement bloqué ")
            
            if((commande == "turn") or (commande == "left")):
                if(valeur > 0):
                    t.left(valeur)
                else :
                    t.left(90)

            if(commande == "right"):
                if(valeur > 0):
                    t.right(valeur)
                else :
                    t.right(90)

            if(commande == "backward"):
                if not table.detection_mur(t.xcor(), t.ycor(), t.heading(), piece) and not table.obstacle_devant(t.xcor(), t.ycor(), t.heading() + 100, piece["obstacle"]):
                    t.forward(valeur * 100)
                else:
                    print("Déplacement bloqué ")
            
            if(commande == "goto"):
                t.goto(valeur)
            
    elif mode == "2":
        table.deplacement_automatique(piece["obstacle"], piece)
    elif mode == "3":
        print("Fin du programme.")
        break

t.done()

