
import cv2
import numpy as np
import time

# ==========================================
# 1. CONFIGURATION
# ==========================================
ID_CAMERA = 0  # 0 pour Mac / 0 ou 1 pour Raspberry Pi
CADENCE_SEC = 0.04

# ==========================================
# 2. PARAMÈTRES HSV 
# ==========================================
plages = {
    "bleu": ((90, 101, 0), (118, 255, 255), (255, 0, 0)), 
    "rouge": ((165, 63, 0), (179, 255, 255), (0, 0, 255))   
}

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))

# ==========================================
# 3. INITIALISATION CAMÉRA
# ==========================================
cap = cv2.VideoCapture(ID_CAMERA)

if not cap.isOpened():
    print(f"Erreur : Impossible d'accéder à la caméra (ID: {ID_CAMERA})")
    exit()

print(f"Lancement de PFR2 sur caméra ID {ID_CAMERA}...")
print("Appuyez sur 'q' pour arrêter.\n")

# 4. BOUCLE DE TRAITEMENT
while True:
    debut_traitement = time.time()
    
    ret, frame = cap.read()
    if not ret:
        print("Erreur de lecture du flux vidéo.")
        break

    # Miroir horizontal (souvent plus naturel sur Mac)
    frame = cv2.flip(frame, 1)

    # Prétraitement
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
    
    detection_globale = []
    
    for nom_couleur, (bas, haut, couleur_affichage) in plages.items():
        masque = cv2.inRange(hsv, bas, haut)
        
        # Nettoyage
        masque = cv2.morphologyEx(masque, cv2.MORPH_CLOSE, kernel)
        masque = cv2.morphologyEx(masque, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            aire = cv2.contourArea(cnt)
            
            if aire > 1000: # Seuil de taille
                perimetre = cv2.arcLength(cnt, True)
                circularite = (4 * np.pi * aire) / (perimetre ** 2) if perimetre > 0 else 0
                
                (x, y), rayon = cv2.minEnclosingCircle(cnt)
                ratio = aire / (np.pi * (rayon ** 2)) if rayon > 0 else 0
                
                if 0.7 < circularite < 1.3 and ratio > 0.60:
                    detection_globale.append(nom_couleur.upper())
                    
                    # Dessin sur le retour vidéo
                    cv2.circle(frame, (int(x), int(y)), int(rayon), couleur_affichage, 3)
                    cv2.putText(frame, nom_couleur, (int(x)-20, int(y)-int(rayon)-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, couleur_affichage, 2)

    # Affichage Terminal
    horodatage = time.strftime('%H:%M:%S')
    if detection_globale:
        # On utilise set() pour ne pas répéter si plusieurs balles de même couleur
        print(f"[{horodatage}] Vu : {', '.join(set(detection_globale))}")
    else:
        print(f"[{horodatage}] Rien de détecté.")

    # Affichage Fenêtre
    cv2.imshow("Test Camera Mac - PFR2", frame)

    # Gestion de la cadence (1 FPS)
    # On calcule le temps restant pour attendre exactement 1 seconde
    temps_ecoule = time.time() - debut_traitement
    temps_attente = max(1, int((CADENCE_SEC - temps_ecoule) * 1000))

    if cv2.waitKey(temps_attente) & 0xFF == ord('q'):
        break

# Nettoyage
cap.release()
cv2.destroyAllWindows()
# Petit fix pour Mac pour bien fermer la fenêtre
for i in range(5): cv2.waitKey(1)