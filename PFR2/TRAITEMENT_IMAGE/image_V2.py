#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 13:43:04 2026

@author: adriennosel
"""

# -*- coding: utf-8 -*-
import cv2
import os
import numpy as np

# CHARGEMENT DE L'IMAGE---------------------------------------------------------
chemin_image = os.path.join("IMG_300", "IMG_5392.jpeg")
img = cv2.imread(chemin_image)

if img is None:
    print(f"Erreur : Impossible de lire l'image à : {chemin_image}")
else:
    hauteur, largeur, canaux = img.shape
    print(f"Image chargée avec succès ! {largeur}x{hauteur}")

    # CONFIGURATION------------------------------------------------------------
    # Conversion en HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Plages de couleurs
    plages = {
        "jaune": ((20, 100, 100), (30, 255, 255), (0, 255, 255)),
        "bleu": ((100, 100, 100), (130, 255, 255), (255, 0, 0)), 
        "rouge": ((0, 100, 100), (10, 255, 255), (0, 0, 255))    
    }
    
    seuil_pixels = 300
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    print(f"--- Analyse des couleurs et formes ---")

    # ANALYSE PAR COULEUR------------------------------------------------------
    for nom_couleur, (bas, haut, couleur_affichage) in plages.items():
        # Masquage et filtre
        # Masquage
        masque = cv2.inRange(hsv, bas, haut)
        
        # Fermeture Morphologique ( boucher les trous)
        kernel_f = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        masque = cv2.morphologyEx(masque, cv2.MORPH_CLOSE, kernel_f)
        
        # Ouverture Morphologique ( nettoyer les points)
        kernel_o = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))
        masque = cv2.morphologyEx(masque, cv2.MORPH_OPEN, kernel_o)
        
        nb_pixels = cv2.countNonZero(masque)
        
        if nb_pixels > seuil_pixels:
            print(f"[{nom_couleur.upper()}] : {nb_pixels} pixels détectés. Analyse de forme...")
            
            # Recherche des contours
            contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                aire = cv2.contourArea(cnt)
                if aire > 200: 
                    perimetre = cv2.arcLength(cnt, True)
                    if perimetre > 0:
                        circularite = (4 * np.pi * aire) / (perimetre ** 2)
                        
                        print(f"  Forme trouvée : Aire={aire:.0f}, Circ={circularite:.2f}")
                        
                        if 0.5 < circularite < 1.5:
                            print(f"  -> BALLE {nom_couleur} trouvée !")

                            # Dessiner le contour
                            (x, y), rayon = cv2.minEnclosingCircle(cnt)
                            cv2.circle(img, (int(x), int(y)), int(rayon), couleur_affichage, 3)
                            cv2.putText(img, f"{nom_couleur}", (int(x)-20, int(y)-int(rayon)-10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, couleur_affichage, 2)

    # GESTION DE LA FENETRE D'AFFICHAGE-----------------------------------------
    cv2.imshow("Detection de balles", img)
    
    print("\nFermeture : Clique sur l'image et appuie sur une touche.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    for i in range(5):
        cv2.waitKey(1)