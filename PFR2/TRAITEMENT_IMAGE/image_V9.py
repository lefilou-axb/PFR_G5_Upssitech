import cv2
import numpy as np
import time

# ==========================================
# 1. PARAMÈTRES PHYSIQUES
# ==========================================
ID_CAMERA = 0
CADENCE_SEC = 0.04

XA0 = 70.0  # Diamètre réel de la balle en mm

# Constantes Arducam 8MP (Capteur IMX219)
f = 3.04             
W_pixels = 1280     
capteur_w_mm = 3.68  
pixel_size = capteur_w_mm / W_pixels 
FOV_H = 62.2 

# Ajustements
CORRECTION_HALO = 2 
K = 1.5 

p1 = f  

# ==========================================
# 2. INITIALISATION
# ==========================================
cap = cv2.VideoCapture(ID_CAMERA, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, W_pixels)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

plages = {
    "bleu": ((90, 101, 0), (118, 255, 255), (255, 0, 0)), 
    "rouge": ((165, 63, 0), (179, 255, 255), (0, 0, 255))   
}

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
kernel_ero = np.ones((3, 3), np.uint8)

print("Lancement sur Raspberry")

while True:
    debut_boucle = time.time()
    ret, frame = cap.read()
    if not ret:
        print("Erreur : Impossible de lire le flux caméra.")
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
    
    for nom_couleur, (bas, haut, couleur_affichage) in plages.items():
        masque = cv2.inRange(hsv, bas, haut)
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
                    # CALCULS DE DISTANCE
                    diametre_pixels = rayon * 2
                    XA1 = diametre_pixels * pixel_size
                    G = XA1 / XA0
                    
                    if G > 0:
                        p0 = (p1 / G) * K
                    else:
                        p0 = 0

                    # CALCUL DE L'ANGLE
                    dx_pixels = x_img - (W_pixels / 2)
                    alpha = (dx_pixels / W_pixels) * FOV_H

                    # AFFICHAGE
                    p0_cm = round(p0 / 10)
                    alpha_deg = round(alpha)
                    print(f"Balle {nom_couleur}: {p0_cm}cm | Angle: {alpha_deg}°")

                    # DESSIN
                    cv2.circle(frame, (int(x_img), int(y_img)), int(rayon), couleur_affichage, 3)
                    cv2.putText(frame, f"{p0_cm}cm / {alpha_deg}deg", (int(x_img), int(y_img) - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("PFR2 - Raspberry Pi", frame)
    
    temps_traitement = (time.time() - debut_boucle) * 1000
    attente = max(1, int((CADENCE_SEC * 1000) - temps_traitement))
    
    if cv2.waitKey(attente) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()






