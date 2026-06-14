# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import cv2
import os

#CHARGEMENT DE L'IMAGE---------------------------------------------------------
chemin_image = os.path.join("IMG_300", "IMG_5389.jpeg")

img = cv2.imread(chemin_image)

if img is None:
    print(f"Erreur : Impossible de lire l'image à : {chemin_image}")
    print("Vérifie que tu as bien lancé Spyder depuis le dossier 'OpenCV'.")
else:
    hauteur, largeur, canaux = img.shape
    print(f"Image chargée avec succès !")
    print(f"Dimensions : {largeur}x{hauteur} pixels")
    print(f"Nombre de canaux (couleurs) : {canaux}")
#CHARGEMENT DE L'IMAGE---------------------------------------------------------

#------------------------------------------------------------------------------

#HISTOGRAMME-------------------------------------------------------------------
    #Conversion en HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #Définition des plages de couleurs (Teinte, Saturation, Valeur)
        # Le Jaune est environ entre 20 et 30 en Teinte (H)
    jaune_bas = (20, 100, 100)
    jaune_haut = (30, 255, 255)

        # Le Bleu est environ entre 100 et 130
    bleu_bas = (100, 100, 100)
    bleu_haut = (130, 255, 255)

        # Le Rouge est particulier (il est au début ET à la fin du cercle chromatique)
    rouge_bas = (0, 100, 100)
    rouge_haut = (10, 255, 255)

    #Masques
    masque_jaune = cv2.inRange(hsv, jaune_bas, jaune_haut)
    masque_bleu = cv2.inRange(hsv, bleu_bas, bleu_haut)
    masque_rouge = cv2.inRange(hsv, rouge_bas, rouge_haut)

    #Histogramme simplifié
    nb_jaune = cv2.countNonZero(masque_jaune)
    nb_bleu = cv2.countNonZero(masque_bleu)
    nb_rouge = cv2.countNonZero(masque_rouge)

    print(f"--- Histogramme des couleurs ---")
    print(f"Pixels Jaunes : {nb_jaune}")
    print(f"Pixels Bleus  : {nb_bleu}")
    print(f"Pixels Rouges : {nb_rouge}")

    #Seuil de détection et hyppothèse
    seuil = 300
    if nb_jaune > seuil:
        print("ALERTE : Balle jaune suspectée !")
    if nb_bleu > seuil:
        print("ALERTE : Balle bleue suspectée !")
    if nb_rouge > seuil:
        print("ALERTE : Balle rouge suspectée !")
#HISTOGRAMME-------------------------------------------------------------------

#------------------------------------------------------------------------------

#GESTION DE LA FENETRE D'AFFICHAGE---------------------------------------------
    cv2.imshow("Image", img)
    print("Appuie sur une touche.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    for i in range(5):
        cv2.waitKey(1)
#GESTION DE LA FENETRE D'AFFICHAGE---------------------------------------------