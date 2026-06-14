#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import time

# ==========================================
# 1. PARAMÈTRES PHYSIQUES & OPTIQUES
# ==========================================
ID_CAMERA = 0
CADENCE_SEC = 0.04

# Dimensions réelles
XA0 = 70.0  # Diamètre réel de la balle en mm

# Caractéristiques Caméra (MacBook)
f = 2.1             
W_pixels = 1280     
capteur_w_mm = 4.8  
pixel_size = capteur_w_mm / W_pixels 
FOV_H = 60.0 # Champ de vision horizontal en degrés

# --- AJUSTEMENTS DE PRÉCISION ---
CORRECTION_HALO = 2 # Pixels retirés sur les bords
K = 1.5             # Coefficient de correction linéaire pour la distance
# ------------------------------------

p1 = f  

# ==========================================
# 2. INITIALISATION
# ==========================================
cap = cv2.VideoCapture(ID_CAMERA)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, W_pixels)

plages = {
    "bleu": ((90, 101, 0), (118, 255, 255), (255, 0, 0)), 
    "rouge": ((165, 63, 0), (179, 255, 255), (0, 0, 255))   
}

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
kernel_ero = np.ones((3, 3), np.uint8)

print("Lancement du programme... Appuyez sur 'q' pour quitter.")

while True:
    debut_boucle = time.time()
    ret, frame = cap.read()
    if not ret: break
    # frame = cv2.flip(frame, 1)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
    
    for nom_couleur, (bas, haut, couleur_affichage) in plages.items():
        masque = cv2.inRange(hsv, bas, haut)
        
        # 1. Nettoyage et érosion de compensation
        masque = cv2.morphologyEx(masque, cv2.MORPH_CLOSE, kernel)
        masque = cv2.erode(masque, kernel_ero, iterations=CORRECTION_HALO)
        
        contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            aire = cv2.contourArea(cnt)
            if aire > 1000:
                perimetre = cv2.arcLength(cnt, True)
                circularite = (4 * np.pi * aire) / (perimetre ** 2) if perimetre > 0 else 0
                (x_img, y_img), rayon = cv2.minEnclosingCircle(cnt)
                ratio = aire / (np.pi * (rayon ** 2)) if rayon > 0 else 0
                
                if 0.7 < circularite < 1.3 and ratio > 0.60:
                    # --- CALCULS OPTIQUES (DISTANCE p0) ---
                    diametre_pixels = rayon * 2
                    XA1 = diametre_pixels * pixel_size
                    G = XA1 / XA0
                    
                    if G > 0:
                        p0_theorique = p1 / G
                        p0 = p0_theorique * K
                    else:
                        p0 = 0

                    # --- CALCUL DE L'ANGLE (alpha) ---
                    # Écart par rapport au centre (positif à droite, négatif à gauche)
                    dx_pixels = x_img - (W_pixels / 2)
                    alpha = (dx_pixels / W_pixels) * FOV_H

                    # --- PRÉPARATION AFFICHAGE ---
                    horodatage = time.strftime('%H:%M:%S')
                    p0_cm = round(p0 / 10)
                    alpha_deg = round(alpha)
                    
                    # Logique de direction
                    direction = "CENTRE"
                    if alpha_deg > 2: direction = "DROITE"
                    elif alpha_deg < -2: direction = "GAUCHE"

                    # Print Terminal
                    print(f"[{horodatage}] {nom_couleur.upper()} -> Dist: {p0_cm}cm | Ang: {alpha_deg}° ({direction}) | XA0: {XA0}mm")

                    # Dessin Caméra
                    cv2.circle(frame, (int(x_img), int(y_img)), int(rayon), couleur_affichage, 3)
                    # Texte Distance
                    cv2.putText(frame, f"{p0_cm}cm", (int(x_img), int(y_img) - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    # Texte Angle
                    cv2.putText(frame, f"{alpha_deg}deg", (int(x_img), int(y_img) + 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("PFR2 - Mesure de distance", frame)
    
    # Gestion de la cadence
    temps_traitement = (time.time() - debut_boucle) * 1000
    attente = max(1, int((CADENCE_SEC * 1000) - temps_traitement))
    
    if cv2.waitKey(attente) & 0xFF == ord('q'): 
        print("Arrêt demandé.")
        break

# Nettoyage final
cap.release()
cv2.destroyAllWindows()
for i in range(5): cv2.waitKey(1)
print("Programme fermé proprement.")





