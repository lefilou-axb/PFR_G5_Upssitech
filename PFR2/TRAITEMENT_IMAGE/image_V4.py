#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np

# CONFIGURATION DE LA SOURCE (Webcam)
cap = cv2.VideoCapture(0)










# PARAMÈTRES
plages = {
    "jaune": ((20, 140, 100), (35, 255, 255), (0, 255, 255)),
    "bleu": ((90, 100, 100), (135, 255, 255), (255, 0, 0)), 
    "rouge": ((0, 140, 80), (15, 255, 255), (0, 0, 255))    
}

kernel_f = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
kernel_o = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
seuil_pixels_total = 300 

print("Démarrage du flux vidéo. Appuie sur 'q' pour quitter.")

# BOUCLE DE TRAITEMENT EN DIRECT
while True:
    # Lecture de l'image
    ret, img = cap.read()
    if not ret:
        print("Erreur de lecture caméra")
        break
    # Variable pour stocker les 3 bits (Rouge, Bleu, Jaune)
    # 000 à chaque nouvelle image
    bits = {"rouge": 0, "bleu": 0, "jaune": 0}
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    for nom_couleur, (bas, haut, couleur_affichage) in plages.items():
        masque = cv2.inRange(hsv, bas, haut)
        
        # filtres morphologiques
        masque = cv2.morphologyEx(masque, cv2.MORPH_CLOSE, kernel_f)
        masque = cv2.morphologyEx(masque, cv2.MORPH_OPEN, kernel_o)
        
        nb_pixels_total = cv2.countNonZero(masque)
        
        if nb_pixels_total > seuil_pixels_total:
            contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                aire = cv2.contourArea(cnt)
                if aire > 100: 
                    perimetre = cv2.arcLength(cnt, True)
                    circularite = (4 * np.pi * aire) / (perimetre ** 2) if perimetre > 0 else 0
                    
                    (x, y), rayon = cv2.minEnclosingCircle(cnt)
                    aire_cercle = np.pi * (rayon ** 2)
                    ratio = aire / aire_cercle if aire_cercle > 0 else 0
                    
                    # Validation balle ?
                    if 0.5 < circularite < 1.5 and ratio > 0.50:
                        # On met le bit à 1 pour cette "couleur"
                        bits[nom_couleur] = 1
                        
                        # Dessin
                        cv2.circle(img, (int(x), int(y)), int(rayon), couleur_affichage, 3)
                        cv2.putText(img, nom_couleur, (int(x)-20, int(y)-int(rayon)-10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, couleur_affichage, 2)

    # AFFICHAGE DES RÉSULTATS
    code_binaire = f"{bits['rouge']}{bits['bleu']}{bits['jaune']}"
    
    # On écrit le code binaire sur l'image pour voir le résultat sans LED
    cv2.putText(img, f"BITS: {code_binaire}", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Affichage de la fenêtre
    cv2.imshow("Analyse en direct", img)

    # Sortie avec la touche 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libération propre
cap.release()
cv2.destroyAllWindows()
for i in range(5): cv2.waitKey(1)