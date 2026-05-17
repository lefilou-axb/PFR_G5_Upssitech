

import cv2
import numpy as np
import time

# ==========================================
# 1. PARAMÈTRES PHYSIQUES & OPTIQUES (VARIABLES)
# ==========================================
ID_CAMERA = 0
CADENCE_SEC = 0.04

# Dimensions réelles
XA0 = 70.0  # Diamètre réel de la balle en mm (À AJUSTER SELON TA BALLE)

# Caractéristiques Caméra (MacBook Air M1 par défaut)
f = 2.1             # Distance focale en mm
W_pixels = 1280     # Résolution horizontale en pixels
capteur_w_mm = 4.8  # Largeur physique du capteur en mm
pixel_size = capteur_w_mm / W_pixels # mm par pixel

# Approximation pour focus fixe
p1 = f  # La distance image-lentille est environ égale à la focale

# ==========================================
# 2. INITIALISATION
# ==========================================
cap = cv2.VideoCapture(ID_CAMERA)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, W_pixels) # On force la résolution pour le calcul

plages = {
    "bleu": ((90, 101, 0), (118, 255, 255), (255, 0, 0)), 
    "rouge": ((165, 63, 0), (179, 255, 255), (0, 0, 255))   
}
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
    
    for nom_couleur, (bas, haut, couleur_affichage) in plages.items():
        masque = cv2.inRange(hsv, bas, haut)
        masque = cv2.morphologyEx(masque, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            aire = cv2.contourArea(cnt)
            if aire > 1000:
                perimetre = cv2.arcLength(cnt, True)
                circularite = (4 * np.pi * aire) / (perimetre ** 2) if perimetre > 0 else 0
                (x_img, y_img), rayon = cv2.minEnclosingCircle(cnt)
                ratio = aire / (np.pi * (rayon ** 2)) if rayon > 0 else 0
                
                if 0.7 < circularite < 1.3 and ratio > 0.60:
                    # --- CALCULS OPTIQUES ---
                    
                    # 1. Taille de l'image sur le capteur (en mm)
                    diametre_pixels = rayon * 2
                    XA1 = diametre_pixels * pixel_size
                    
                    # 2. Grandissement transversal
                    # G = XA1 / XA0 = p1 / p0
                    G = XA1 / XA0
                    
                    # 3. Distance de l'objet (p0)
                    # p0 = p1 / G (issu de G = p1/p0)
                    if G > 0:
                        p0 = p1 / G
                    else:
                        p0 = 0

                    # --- AFFICHAGE ---
                    horodatage = time.strftime('%H:%M:%S')
                    print(f"[{horodatage}] COULEUR: {nom_couleur.upper()}")
                    print(f"    - Distance : {round(p0/10):.1f} cm")
                    print("-" * 30)

                    cv2.circle(frame, (int(x_img), int(y_img)), int(rayon), couleur_affichage, 3)
                    cv2.putText(frame, f"{int(p0/10)}cm", (int(x_img), int(y_img)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("PFR2 - Mesure de distance", frame)
    if cv2.waitKey(int(CADENCE_SEC * 1000)) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
for i in range(5):
    cv2.waitKey(1)
    
    
    
    
    
    
    
    
    
    