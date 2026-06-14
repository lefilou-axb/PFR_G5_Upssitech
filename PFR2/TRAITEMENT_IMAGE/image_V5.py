#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#image_V3 créé toutes les image modifiées avec les balles entourées

import cv2
import os
import numpy as np
import glob

# 1. CONFIGURATION DES DOSSIERS
dossier_source = "IMG_300"
dossier_destination = "IMG_300_ID"

if not os.path.exists(dossier_destination):
    os.makedirs(dossier_destination)

# 2. PARAMÈTRES
plages = {
    
    "bleu": ((90, 101, 0), (118, 255, 255), (255, 0, 0)), 
    "rouge": ((165, 63, 0), (179, 255, 255), (0, 0, 255))   
}


kernel_f = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
kernel_o = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))

seuil_pixels_total = 300

# 3. TRAITEMENT
liste_images = glob.glob(os.path.join(dossier_source, "*.jpeg"))
print(f"Analyse de {len(liste_images)} images...\n")

for chemin_img in liste_images:
    img = cv2.imread(chemin_img)
    nom_fichier = os.path.basename(chemin_img)
    if img is None: continue

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    print(f"--- Fichier : {nom_fichier} ---")
    
    for nom_couleur, (bas, haut, couleur_affichage) in plages.items():
        masque = cv2.inRange(hsv, bas, haut)
        
        # Nettoyage morphologique
        masque = cv2.morphologyEx(masque, cv2.MORPH_CLOSE, kernel_f)
        masque = cv2.morphologyEx(masque, cv2.MORPH_OPEN, kernel_o)
        
        nb_pixels_total = cv2.countNonZero(masque)
        
        if nb_pixels_total > seuil_pixels_total:
            contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            print(f"  Couleur {nom_couleur.upper()} ({nb_pixels_total} px total) :")
            
            for i, cnt in enumerate(contours):
                aire = cv2.contourArea(cnt)
                
                # 1. SEUIL DE TAILLE
                if aire > 1000:  
                    perimetre = cv2.arcLength(cnt, True)
                    circularite = (4 * np.pi * aire) / (perimetre ** 2) if perimetre > 0 else 0
                    
                    (x, y), rayon = cv2.minEnclosingCircle(cnt)
                    aire_cercle = np.pi * (rayon ** 2)
                    ratio = aire / aire_cercle if aire_cercle > 0 else 0
                    
                # 2. FILTRE DE FORME 
                    if 0.7 < circularite < 1.3 and ratio > 0.60:
                        statut = "VALIDE (BALLE)"
                        cv2.circle(img, (int(x), int(y)), int(rayon), couleur_affichage, 3)
                        cv2.putText(img, nom_couleur, (int(x)-20, int(y)-int(rayon)-10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, couleur_affichage, 2)
                    else:
                        statut = "REJETÉ (FORME)"
    cv2.imwrite(os.path.join(dossier_destination, nom_fichier), img)

print("\n--- Analyse terminée. Résultats dans le dossier IMG_300_ID ---")