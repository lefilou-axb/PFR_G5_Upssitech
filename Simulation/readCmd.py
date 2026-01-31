import turtle as t
import table

#Initialisation de la piece
HD = 0
HG = 0
BD = 0
BG = 0

balle_Green = {
    "nom" : "obstacle1",
    "type" : "cercle",
    "positionCentre" : (0,0),
    "dimension_Rayon_Cote" : 20,
    "couleur" : 'green',
    "epaisseur": 10
}

piece1 = {
    "nom": "piece1",
    "dimensions": (400,400), #(Largeur,Longueur) de la piece
    "positionCoinHautDroit": (200,200), #Position du coin haut droit (x_HD, y_HD)
    "obstacle": [] #liste vide à renseigner plus tard
}

piece2 = {
    "nom": "piece1",
    "dimensions": (400,400), #(Largeur,Longueur) de la piece
    "positionCoinHautDroit": (200,200), #Position du coin haut droit (x_HD, y_HD)
    "obstacle": [balle_Green] #liste vide à renseigner plus tard
}



# Initialisation de la liste qui va contenir les commandes du fichier
cmd_list = []
depart = (50,50)

# Lecture du fichier et remplissage de la liste des commandes
with open("../IHM/commands.txt","r") as file:
    for ligne in file:
        ligne = ligne.strip()
        #print(ligne)
        cmd_list.append(ligne)
#print(cmd_list)

table.tracerPiece(piece2)

# Déplacement du robot
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
        if(valeur == 0):
            t.goto(balle_Green["positionCentre"])
        else :
            print("Objet inconnu")
    
t.up()
t.done()


