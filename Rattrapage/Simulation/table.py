# ***************************************************************************************
#   Nom : Haegel                                                                        *
#   Prénom : Lucas                                                                      *
#   Définition : Ce fichier contient les fonctions de traçage de pieces et d'obstacles. *
#                                                                                       *
# ***************************************************************************************

# bibliothèque
import turtle as t
import os
import glob
import math

HD = 0
BD = 0 
HG = 0
BG = 0
def lecturePiece(chemin_fichier):
    try:
        with open(chemin_fichier) as f:
            for ligne in f :
                ligne = ligne.strip()

                if not ligne:
                    continue
                
                #Utilisation la virgule pour terminer la ligne
                partie = [p.strip() for p in ligne.split(",")]

                if len(partie) != 5:
                    print("Format d'objet invalide")
                    return None

                nom = partie[0]
                largeur = int(partie[1])
                longueur = int(partie[2])
                x_HD = int(partie[3])
                y_HD = int(partie[4])
                
                piece = {
                    "nom" : nom,
                    "dimensions" : (largeur, longueur),
                    "positionCoinHautDroit" : (x_HD, y_HD),
                    "obstacle" : []
                }

                print(f"Piece {nom} chargée")
                return piece

    except FileNotFoundError:
        print("Piece introuvable : {chemin_fichier}")
        return None

    except ValueError:
        print("Valeur invalide dans {chemin_fichier}")
        return None

def lectureObjet(chemin_fichier):
    try:
        with open(chemin_fichier) as f:
            for ligne in f:
                ligne = ligne.strip()

                if not ligne:
                    continue
                
                #Utilisation la virgule pour terminer la ligne
                partie = [p.strip() for p in ligne.split(",")]

                if len(partie) != 5:
                    print("Format d'objet invalide")
                    return None
                
                couleur = partie[0]
                position = (int(partie[1]), int(partie[2]))
                forme = partie[3]
                dimension = partie[4]

                fichierObjet = os.path.basename(chemin_fichier)
                nom_objet = fichierObjet.replace(".txt", "").replace("_", "").lower()
                
                obstacle = {
                    "nom" : nom_objet,
                    "type" : forme,
                    "positionCentre" : position,
                    "dimension_Rayon_Cote" : int(dimension),
                    "couleur" : couleur,
                    "epaisseur" : 10
                }

                print(f"Objet {nom_objet} chargé")
                return obstacle

    except FileNotFoundError:
        print(f"Fichier introuvable : {chemin_fichier}")
        return None
    
    except ValueError:
        print(f"Valeur invalide dans {chemin_fichier} : {ValueError}")
        return None

def chargerObjet(dossier="."):
    obstacles = []

    #Chargement des fichiers
    pattern = os.path.join(dossier, "Objet_*.txt")
    fichiers = sorted(glob.glob(pattern))

    if not fichiers:
        print(f"Aucun fichier Objet_*.txt trouvé dans : {dossier}")
        return obstacles
    
    print(f"{len(fichiers)} fichier objet trouvé :")
    for chemin in fichiers:
        obstacle = lectureObjet(chemin)
        if obstacle is not None:
            obstacles.append(obstacle)
    
    print(f"{len(obstacles)} objet(s) chargé(s).")
    return obstacles

def tracerPiece(la_piece):
    global HD, BD, HG, BG

    #Angle de rotation
    angle = 90

    HD = la_piece["positionCoinHautDroit"]
    BD = [la_piece["positionCoinHautDroit"][0], la_piece["positionCoinHautDroit"][1]-la_piece["dimensions"][1]]
    BG = [la_piece["positionCoinHautDroit"][0]-la_piece["dimensions"][0], la_piece["positionCoinHautDroit"][1]-la_piece["dimensions"][1]]
    HG = [la_piece["positionCoinHautDroit"][0]-la_piece["dimensions"][0], la_piece["positionCoinHautDroit"][1]]

    #Initialisation de la variable contenant les coins de la piece
    coin_piece = [HD, BD, BG, HG]   
    #print(coin_piece) #Affichage de la position des coins    

    # néttoyage de la table traçante
    t.clearscreen()

    # Stylet en position haute - pas de traçage
    t.up()

    # déplacement au coin Haut Droit 
    t.goto(coin_piece[0])

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
        #print("HD") #TRACE DE DEBUG
    if obstacle["positionCentre"][0]+obstacle["dimension_Rayon_Cote"]+5 > BD[0] or obstacle["positionCentre"][1]-5 < BD[1] :
        obstaclePossible = False
        #print("BD") #TRACE DE DEBUG
    if obstacle["positionCentre"][0]+obstacle["dimension_Rayon_Cote"]-5 < HG[0] or obstacle["positionCentre"][1]-5 > HG[1] :
        obstaclePossible = False
        #print("HG") #TRACE DE DEBUG
    if obstacle["positionCentre"][0]-obstacle["dimension_Rayon_Cote"]-5 < BG[0] or obstacle["positionCentre"][1]+5 < BG[1] :
        obstaclePossible = False
        #print("BG") #TRACE DE DEBUG
    if obstaclePossible == False :
            print("L'obstacle ne peut pas être placé, il est hors dimension de la pièce.")
            #print("Obstacle voulu en : ", obstacle["positionCentre"])
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
        print(f"Obstacle tracé en {obstacle['positionCentre']}")
        #piece["obstacle"].append(obstacle)
    
def obstacle_devant(x, y, angle, obstacles, distance=10):

    #Distance à 10pixels devant le robot selon son angle
    xdevant = x + distance * math.cos(math.radians(angle))
    ydevant = y + distance * math.sin(math.radians(angle))

    for obstacle in obstacles:
        objet_x = obstacle["positionCentre"][0]
        objet_y = obstacle["positionCentre"][1]
        dimension_objet = obstacle["dimension_Rayon_Cote"]

        if obstacle["type"] == "cercle":
            distance_cercle = math.sqrt((xdevant - objet_x)**2 + (ydevant - objet_y)**2)
            if distance_cercle <= dimension_objet:
                print(f"Obstacle '{obstacle['nom']}' détecté.")
                return True

        if obstacle["type"] == "carre":
            # Vérifier si le point est dans le carré
            if objet_x <= xdevant <= objet_x + dimension_objet and objet_y <= ydevant <= objet_y + dimension_objet:
                print(f"Obstacle '{obstacle['nom']}' détecté.")
                return True

    return False
