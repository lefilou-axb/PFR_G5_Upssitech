# ***************************************************************************************
#   Nom : Haegel                                                                        *
#   Prénom : Lucas                                                                      *
#   Définition : Ce fichier contient les fonctions de traçage de pieces et d'obstacles. *
#                                                                                       *
# ***************************************************************************************

# bibliothèque
import turtle as t

def tracerPiece(la_piece):
    #Test pour savoir si la piece est carré ou non
    if la_piece["dimensions"][0] == la_piece["dimensions"][1]: #Test sur la valeur du constituant
        print("Piece carré de dimension : ", la_piece["dimensions"][0])
    else :
        print("Piece non carré, largeur = ", la_piece["dimensions"][0], " et longueur = ", la_piece["dimensions"][1])


    #Initialisation de la position des coins de la piece
    global HD
    global BD
    global HG
    global BG
    HD = la_piece["positionCoinHautDroit"]
    BD = [la_piece["positionCoinHautDroit"][0], la_piece["positionCoinHautDroit"][1]-la_piece["dimensions"][1]]
    BG = [la_piece["positionCoinHautDroit"][0]-la_piece["dimensions"][0], la_piece["positionCoinHautDroit"][1]-la_piece["dimensions"][1]]
    HG = [la_piece["positionCoinHautDroit"][0]-la_piece["dimensions"][0], la_piece["positionCoinHautDroit"][1]]

    #Initialisation de la variable contenant les coins de la piece
    coin_piece = [HD, BD, BG, HG]   

    print(coin_piece) #Affichage de la position des coins    


    # Prise en compte d'une pièce
    #Angle de rotation
    angle = 90

    # néttoyage de la table traçante
    t.clearscreen()

    # Stylet en position haute - pas de traçage
    t.up()

    # position du coin Haut Droit
    # Dans le dictionnaire

    # déplacement au coin Haut Droit 
    t.goto(coin_piece[0])


    # Dimensions de la pièce carrée
    # Dans le dictionnaire

    # Données pour le traçage
    t.width(5)                  # largeur du trait
    t.color('blue')             # couleur du trait
    t.down()                    # stylet en position basse pour le traçage

    # tracer les contours de la pièce
    for i in range(5):
        i = i%4
        t.goto(coin_piece[i])
        t.right(angle)

    t.up()

    # Ajout des obstacles
    if(len(la_piece["obstacle"]) > 0) :
        for i in range(len(la_piece["obstacle"])) :
            ajouter_obstacle(la_piece["obstacle"][i],la_piece)

def ajouter_obstacle(obstacle,piece):
    obstaclePossible = True #Possibilité de positionner l'obstacle
    #Test pour savoir si on peut poser l'obstacle
    if obstacle["positionCentre"][0]+obstacle["dimension_Rayon_Cote"]+5 > HD[0] or obstacle["positionCentre"][1]+5 > HD[1] :
        obstaclePossible = False
        print("HD") #TRACE DE DEBUG
    if obstacle["positionCentre"][0]+obstacle["dimension_Rayon_Cote"]+5 > BD[0] or obstacle["positionCentre"][1]-5 < BD[1] :
        obstaclePossible = False
        print("BD") #TRACE DE DEBUG
    if obstacle["positionCentre"][0]+obstacle["dimension_Rayon_Cote"]-5 < HG[0] or obstacle["positionCentre"][1]-5 > HG[1] :
        obstaclePossible = False
        print("HG") #TRACE DE DEBUG
    if obstacle["positionCentre"][0]-obstacle["dimension_Rayon_Cote"]-5 < BG[0] or obstacle["positionCentre"][1]+5 < BG[1] :
        obstaclePossible = False
        print("BG") #TRACE DE DEBUG
    if obstaclePossible == False :
            print("L'obstacle ne peut pas être placé, il est hors dimension de la pièce.")
            print("Obstacle voulu en : ", obstacle["positionCentre"])
    else :
        # Traçage de l'obstacle
        t.width(obstacle["epaisseur"])                    # largeur du trait des ouvertures
        t.up()                                              # stylet en position haute  
        t.goto(obstacle["positionCentre"])                               # déplacement jusqu'au la position de l'obstacle 1
        
        t.width(t.width(obstacle["epaisseur"]))      
        t.color(obstacle["couleur"])
    
        if obstacle["type"] == 'cercle' :
            #if obstacle["positionCentre"][1] > HD:
            t.forward(obstacle["dimension_Rayon_Cote"])
            t.down()                           # stylet en position basse
            t.begin_fill()
            t.circle(obstacle["dimension_Rayon_Cote"])
            t.end_fill()
        
        if obstacle["type"] == 'carre' :
            #if obstacle["positionCentre"][1] > HD:
            t.forward(obstacle["dimension_Rayon_Cote"])
            t.down()                           # stylet en position basse
            t.begin_fill()
            for i in range(4):
                t.forward(obstacle["dimension_Rayon_Cote"])
                t.right(90)
            t.end_fill()
                  
        t.up()                         # retour en position haute
        print("Obstacle tracé en : ", obstacle["positionCentre"])
        piece["obstacle"].append(obstacle)
    

def tracer_obstacles_piece(piece):
    for i in range(len(piece["obstacle"])):
        print(piece["obstacle"][i]["nom"])