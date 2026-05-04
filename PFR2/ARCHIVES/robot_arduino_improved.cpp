#include <AFMotor.h>

// ==================== CONFIGURATION CAPTEURS ====================
// Capteur 1 (avant1)
#define TRIG1 22
#define ECHO1 24

// Capteur 2 (arrière)
#define TRIG2 48
#define ECHO2 50

// Capteur 3 (avant2)
#define TRIG3 41
#define ECHO3 38

// ==================== CALIBRATION - À MODIFIER PAR VOS TESTS ====================
// INSTRUCTIONS DE CALIBRAGE :
// 1. Décommenter la section TEST au bas du code
// 2. Faire avancer le robot de 1 mètre et mesurer le temps exact (en ms)
// 3. Calculer : DISTANCE_RATIO = 1000 / temps_en_ms
//    Exemple : si robot met 5000ms pour 1m → DISTANCE_RATIO = 1000 / 5000 = 0.2 m/ms
//
// 4. Faire tourner le robot de 90° et mesurer le temps exact
// 5. Calculer : ANGLE_RATIO = 90 / temps_en_ms
//    Exemple : si robot met 750ms pour 90° → ANGLE_RATIO = 90 / 750 = 0.12 deg/ms

#define DISTANCE_RATIO 0.4  // À CALIBRER : mètres par milliseconde (exemple: 0.4 m/s)
#define ANGLE_RATIO 0.12    // À CALIBRER : degrés par milliseconde (exemple: 0.12 deg/ms)
#define OBSTACLE_DISTANCE 30.0 // Distance minimale avant arrêt (cm)

// ==================== MOTEURS ====================
AF_DCMotor m1(1);
AF_DCMotor m2(2);
AF_DCMotor m3(3);
AF_DCMotor m4(4);

// ==================== VARIABLES GLOBALES ====================
int bluetoothCommand = 0;
unsigned long moveStartTime = 0;
unsigned long moveDuration = 0;
bool isMoving = false;
int currentMoveType = 0; // 1=forward, 2=backward, 3=left, 4=right
String commandBuffer = "";
int motorSpeed = 200; // Vitesse par défaut

// ==================== FONCTIONS MOTEURS ====================
void avancer() {
  m1.run(FORWARD);
  m2.run(FORWARD);
  m3.run(FORWARD);
  m4.run(FORWARD);
}

void reculer() {
  m1.run(BACKWARD);
  m2.run(BACKWARD);
  m3.run(BACKWARD);
  m4.run(BACKWARD);
}

void gauche() {
  m1.run(BACKWARD);
  m2.run(FORWARD);
  m3.run(FORWARD);
  m4.run(BACKWARD);
}

void droite() {
  m1.run(FORWARD);
  m2.run(BACKWARD);
  m3.run(BACKWARD);
  m4.run(FORWARD);
}

void stopMoteurs() {
  m1.run(RELEASE);
  m2.run(RELEASE);
  m3.run(RELEASE);
  m4.run(RELEASE);
  isMoving = false;
}

void setMotorSpeed(int speed) {
  motorSpeed = speed;
  m1.setSpeed(speed);
  m2.setSpeed(speed);
  m3.setSpeed(speed);
  m4.setSpeed(speed);
}

// ==================== MESURE DISTANCE ====================
float mesurerDistance(int trigPin, int echoPin) {
  long duree;
  float distance;

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duree = pulseIn(echoPin, HIGH);
  distance = duree * 0.034 / 2;

  return distance;
}

// ==================== MOUVEMENT AVEC DURÉE ====================
// Fonction pour avancer une distance en mètres
void avancerDistance(float distanceMetres) {
  moveDuration = (unsigned long)(distanceMetres / DISTANCE_RATIO); // Convertir distance en temps
  moveStartTime = millis();
  isMoving = true;
  currentMoveType = 1;
  
  Serial.print(">> Avance de ");
  Serial.print(distanceMetres);
  Serial.print("m (");
  Serial.print(moveDuration);
  Serial.println("ms)");
  
  avancer();
}

// Fonction pour reculer une distance en mètres
void reculerDistance(float distanceMetres) {
  moveDuration = (unsigned long)(distanceMetres / DISTANCE_RATIO);
  moveStartTime = millis();
  isMoving = true;
  currentMoveType = 2;
  
  Serial.print(">> Recule de ");
  Serial.print(distanceMetres);
  Serial.print("m (");
  Serial.print(moveDuration);
  Serial.println("ms)");
  
  reculer();
}

// Fonction pour tourner d'un angle en degrés
void tournerAngle(float angleDegres) {
  moveDuration = (unsigned long)(angleDegres / ANGLE_RATIO); // Convertir angle en temps
  moveStartTime = millis();
  isMoving = true;
  
  if (angleDegres > 0) {
    currentMoveType = 4; // Droite
    Serial.print(">> Tourne à droite de ");
  } else {
    currentMoveType = 3; // Gauche
    Serial.print(">> Tourne à gauche de ");
  }
  
  Serial.print(abs(angleDegres));
  Serial.print("° (");
  Serial.print(moveDuration);
  Serial.println("ms)");
  
  if (angleDegres > 0) {
    droite();
  } else {
    gauche();
  }
}

// ==================== VÉRIFICATION OBSTACLES ====================
bool verifierObstacles() {
  float cpt1 = mesurerDistance(TRIG1, ECHO1);
  float cpt3 = mesurerDistance(TRIG3, ECHO3);
  float cpt2 = mesurerDistance(TRIG2, ECHO2);
  
  // Afficher les capteurs
  Serial.print("Capteur 1 : ");
  Serial.print(cpt1);
  Serial.print(" cm | Capteur 3 : ");
  Serial.print(cpt3);
  Serial.print(" cm | Capteur 2 : ");
  Serial.print(cpt2);
  Serial.println(" cm");
  
  // Vérifier selon le type de mouvement
  if (currentMoveType == 1 || currentMoveType == 1) { // Avance ou recule
    if (currentMoveType == 1 && (cpt1 < OBSTACLE_DISTANCE || cpt3 < OBSTACLE_DISTANCE)) {
      Serial.println("⚠️  OBSTACLE DÉTECTÉ EN AVANT !");
      return false;
    }
    if (currentMoveType == 2 && cpt2 < OBSTACLE_DISTANCE) {
      Serial.println("⚠️  OBSTACLE DÉTECTÉ EN ARRIÈRE !");
      return false;
    }
  }
  
  return true;
}

// ==================== TRAITEMENT COMMANDES ====================
void traiterCommande(String commande) {
  commande.trim();
  
  // Parser la commande : "forward 2.00" ou "right 90.00"
  int espaceIndex = commande.indexOf(' ');
  if (espaceIndex == -1) return; // Format invalide
  
  String cmd = commande.substring(0, espaceIndex);
  String valeurStr = commande.substring(espaceIndex + 1);
  float valeur = valeurStr.toFloat();
  
  Serial.print("📋 Commande reçue: [");
  Serial.print(cmd);
  Serial.print("] [");
  Serial.print(valeur);
  Serial.println("]");
  
  if (cmd == "forward" || cmd == "avance") {
    avancerDistance(valeur);
  }
  else if (cmd == "backward" || cmd == "recule") {
    reculerDistance(valeur);
  }
  else if (cmd == "right" || cmd == "droite") {
    tournerAngle(valeur);
  }
  else if (cmd == "left" || cmd == "gauche") {
    tournerAngle(-valeur);
  }
  else if (cmd == "stop") {
    stopMoteurs();
  }
  else {
    Serial.println("❌ Commande inconnue !");
  }
}

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);   // Communication PC/RPi
  Serial1.begin(115200);  // Bluetooth

  m1.setSpeed(motorSpeed);
  m2.setSpeed(motorSpeed);
  m3.setSpeed(motorSpeed);
  m4.setSpeed(motorSpeed);

  stopMoteurs();

  pinMode(TRIG1, OUTPUT);
  pinMode(ECHO1, INPUT);

  pinMode(TRIG2, OUTPUT);
  pinMode(ECHO2, INPUT);

  pinMode(TRIG3, OUTPUT);
  pinMode(ECHO3, INPUT);
  
  Serial.println("\n========== ROBOT DÉMARRÉ ==========");
  Serial.print("Distance Ratio: ");
  Serial.print(DISTANCE_RATIO);
  Serial.print(" m/ms | Angle Ratio: ");
  Serial.print(ANGLE_RATIO);
  Serial.println(" deg/ms");
  Serial.println("Prêt à recevoir des commandes...\n");
}

// ==================== LOOP PRINCIPAL ====================
void loop() {
  
  // ===== 1. VÉRIFIER COMMANDES BLUETOOTH (Priorité haute) =====
  if (Serial1.available() > 0) {
    bluetoothCommand = Serial1.read();
    
    Serial.print("📱 Commande Bluetooth reçue : ");
    Serial.println(bluetoothCommand);
    
    // Stopper tout mouvement en cours
    if (isMoving) {
      stopMoteurs();
      Serial.println("⛔ Mouvement interrompu par Bluetooth");
    }
    
    // Exécuter la commande Bluetooth immédiatement
    switch (bluetoothCommand) {
      case 1: // Avancer
        if (verifierObstacles()) {
          avancer();
        } else {
          stopMoteurs();
        }
        break;
        
      case 2: // Reculer
        reculer();
        break;
        
      case 3: // Tourner à gauche
        gauche();
        delay(500);
        stopMoteurs();
        break;
        
      case 4: // Tourner à droite
        droite();
        delay(500);
        stopMoteurs();
        break;
        
      case 5:
      default:
        stopMoteurs();
        break;
    }
    
    bluetoothCommand = 0; // Reset
  }
  
  // ===== 2. RECEVOIR COMMANDES DEPUIS FICHIER (RPi) =====
  if (Serial.available() > 0) {
    char c = Serial.read();
    
    if (c == '\n') {
      // Fin de ligne = traiter la commande
      if (commandBuffer.length() > 0) {
        traiterCommande(commandBuffer);
        commandBuffer = "";
      }
    } else {
      commandBuffer += c;
    }
  }
  
  // ===== 3. GÉRER LE MOUVEMENT EN COURS =====
  if (isMoving) {
    unsigned long elapsedTime = millis() - moveStartTime;
    
    // Vérifier les obstacles pendant le mouvement
    if (!verifierObstacles()) {
      Serial.println("❌ ARRÊT D'URGENCE - Obstacle détecté!");
      stopMoteurs();
      delay(500);
      
      // Tenter un contournement automatique
      if (currentMoveType == 1) { // Si avait une obstacle en avant
        reculer();
        delay(200);
        stopMoteurs();
        delay(200);
        
        float cpt1 = mesurerDistance(TRIG1, ECHO1);
        float cpt3 = mesurerDistance(TRIG3, ECHO3);
        
        if (cpt1 > cpt3) {
          droite();
        } else {
          gauche();
        }
        delay(750);
        stopMoteurs();
      }
      
      return;
    }
    
    // Vérifier si le mouvement est terminé
    if (elapsedTime >= moveDuration) {
      stopMoteurs();
      Serial.println("✅ Mouvement terminé");
    }
  }
  
  delay(100); // Petite pause pour éviter les lectures trop rapides
}

// ==================== CODE DE TEST (À DÉCOMMENTER) ====================
/*
 * INSTRUCTIONS DE CALIBRAGE :
 * 1. Décommenter les lignes ci-dessous
 * 2. Uploader le code
 * 3. Ouvrir le moniteur série à 115200
 * 4. Tester les mouvements et ajuster DISTANCE_RATIO et ANGLE_RATIO
 * 
 * EXEMPLE DE TEST :
 * 
 * void testCalibration() {
 *   Serial.println("TEST 1: Avance 1 mètre");
 *   avancer();
 *   delay(5000);  // À adapter jusqu'à ce que le robot avance 1m
 *   stopMoteurs();
 *   delay(2000);
 *   
 *   Serial.println("TEST 2: Tourne 90°");
 *   droite();
 *   delay(750);  // À adapter jusqu'à 90°
 *   stopMoteurs();
 * }
 * 
 * // Appeler testCalibration() dans setup() pour lancer les tests
 */
