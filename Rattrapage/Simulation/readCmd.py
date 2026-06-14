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

#########################
#Initialisation des pieces & des obstacles


#########################

piece = table.lecturePiece(os.path.join(Dossier_simulation, "Piece_1.txt"))

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
piece["obstacle"] = table.chargerObjet(Dossier_simulation)


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

# Déplacement du robot
#Initialisation des déplacements
t.goto(depart)
t.width(2)
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
        t.forward(valeur*100)
    
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
        t.backward(valeur)
    
    if(commande == "goto"):
        t.goto(valeur)
    
t.up()
t.done()


