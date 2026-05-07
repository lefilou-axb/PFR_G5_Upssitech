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
#define DISTANCE_RATIO 0.0008  // À CALIBRER : mètres par milliseconde
#define ANGLE_RATIO 0.09       // À CALIBRER : degrés par milliseconde
#define OBSTACLE_DISTANCE 30.0 // Distance minimale avant arrêt (cm)

// ==================== MOTEURS ====================
AF_DCMotor m1(1);
AF_DCMotor m2(2);
AF_DCMotor m3(3);
AF_DCMotor m4(4);

// ==================== MACHINE À ÉTATS ====================
// États possibles du robot
#define ETAT_ARRET          0
#define ETAT_AVANCE         1
#define ETAT_RECULE         2
#define ETAT_GAUCHE         3
#define ETAT_DROITE         4
#define ETAT_EVITEMENT_RECUL  5   // Phase 1 évitement : reculer
#define ETAT_EVITEMENT_PAUSE  6   // Phase 2 évitement : pause
#define ETAT_EVITEMENT_TOURNE 7   // Phase 3 évitement : tourner
#define ETAT_EVITEMENT_REPREND 8  // Phase 4 évitement : reprendre avance

// ==================== VARIABLES GLOBALES ====================
int etatRobot = ETAT_ARRET;
int etatApresEvitement = ETAT_ARRET; // État à reprendre après évitement
bool commandeBT_continue = false;    // true = commande BT sans durée (ex: avancer indéfiniment)

unsigned long moveStartTime = 0;
unsigned long moveDuration = 0;       // 0 = mouvement infini (BT)

int directionEvitement = 0;           // +1 = droite, -1 = gauche

String commandBuffer = "";
int motorSpeed = 200;

// ==================== TÉLÉMÉTRIE CAPTEURS ====================
unsigned long lastSensorSend = 0;
#define SENSOR_SEND_INTERVAL 500  // Envoyer les distances toutes les 500ms

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
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duree = pulseIn(echoPin, HIGH, 30000); // timeout 30ms pour éviter blocage
  if (duree == 0) return 999.0; // Pas d'écho = pas d'obstacle détecté
  return duree * 0.034 / 2;
}

// ==================== DÉMARRAGE MOUVEMENTS (non-bloquants) ====================
void demarrerAvance(unsigned long dureeMs, bool infini) {
  commandeBT_continue = infini;
  moveDuration = dureeMs;
  moveStartTime = millis();
  etatRobot = ETAT_AVANCE;
  avancer();
  Serial.println(">> Avance");
}

void demarrerRecul(unsigned long dureeMs, bool infini) {
  commandeBT_continue = infini;
  moveDuration = dureeMs;
  moveStartTime = millis();
  etatRobot = ETAT_RECULE;
  reculer();
  Serial.println(">> Recule");
}

void demarrerGauche(unsigned long dureeMs) {
  commandeBT_continue = false;
  moveDuration = dureeMs;
  moveStartTime = millis();
  etatRobot = ETAT_GAUCHE;
  gauche();
  Serial.println(">> Tourne gauche");
}

void demarrerDroite(unsigned long dureeMs) {
  commandeBT_continue = false;
  moveDuration = dureeMs;
  moveStartTime = millis();
  etatRobot = ETAT_DROITE;
  droite();
  Serial.println(">> Tourne droite");
}

// Lance la séquence d'évitement (recul → pause → rotation → reprise)
void lancerEvitement(float cpt1, float cpt3) {
  stopMoteurs();
  directionEvitement = (cpt1 > cpt3) ? 1 : -1; // +1 = droite, -1 = gauche
  etatApresEvitement = ETAT_AVANCE;             // On reprendra l'avance après
  moveStartTime = millis();
  moveDuration = 300; // Durée du recul d'évitement
  etatRobot = ETAT_EVITEMENT_RECUL;
  reculer();
  Serial.println("!! Obstacle détecté → évitement");
}

// ==================== TRAITEMENT COMMANDES SÉRIE (RPi) ====================
void traiterCommande(String commande) {
  commande.trim();
  int espaceIndex = commande.indexOf(' ');
  if (espaceIndex == -1) return;

  String cmd = commande.substring(0, espaceIndex);
  float valeur = commande.substring(espaceIndex + 1).toFloat();

  Serial.print("Commande reçue: ["); Serial.print(cmd);
  Serial.print("] ["); Serial.print(valeur); Serial.println("]");

  if (cmd == "forward" || cmd == "avance") {
    unsigned long duree = (unsigned long)(valeur / DISTANCE_RATIO);
    demarrerAvance(duree, false);
  }
  else if (cmd == "backward" || cmd == "recule") {
    unsigned long duree = (unsigned long)(valeur / DISTANCE_RATIO);
    demarrerRecul(duree, false);
  }
  else if (cmd == "right" || cmd == "droite") {
    unsigned long duree = (unsigned long)(abs(valeur) / ANGLE_RATIO);
    demarrerDroite(duree);
  }
  else if (cmd == "left" || cmd == "gauche") {
    unsigned long duree = (unsigned long)(abs(valeur) / ANGLE_RATIO);
    demarrerGauche(duree);
  }
  else if (cmd == "stop") {
    etatRobot = ETAT_ARRET;
    commandeBT_continue = false;
    stopMoteurs();
  }
  else {
    Serial.println("Commande inconnue !");
  }
}

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);

  m1.setSpeed(motorSpeed);
  m2.setSpeed(motorSpeed);
  m3.setSpeed(motorSpeed);
  m4.setSpeed(motorSpeed);

  stopMoteurs();
  etatRobot = ETAT_ARRET;

  pinMode(TRIG1, OUTPUT); pinMode(ECHO1, INPUT);
  pinMode(TRIG2, OUTPUT); pinMode(ECHO2, INPUT);
  pinMode(TRIG3, OUTPUT); pinMode(ECHO3, INPUT);

  Serial.println("\n========== ROBOT DÉMARRÉ ==========");
  Serial.println("Prêt à recevoir des commandes...\n");
}

// ==================== LOOP PRINCIPAL ====================
void loop() {

  // ===== 1. LIRE COMMANDES BLUETOOTH =====
  if (Serial1.available() > 0) {
    int btCmd = Serial1.read();
    Serial.print("BT reçu : "); Serial.println(btCmd);

    // Annuler tout mouvement en cours (sauf évitement actif)
    if (etatRobot != ETAT_EVITEMENT_RECUL &&
        etatRobot != ETAT_EVITEMENT_PAUSE &&
        etatRobot != ETAT_EVITEMENT_TOURNE) {
      stopMoteurs();
      etatRobot = ETAT_ARRET;
      commandeBT_continue = false;
    }

    switch (btCmd) {
      case 1: // Avancer en continu (infini, arrêt sur obstacle)
        demarrerAvance(0, true);
        break;
      case 2: // Reculer en continu
        demarrerRecul(0, true);
        break;
      case 3: // Tourner gauche 500ms
        demarrerGauche(1180);
        break;
      case 4: // Tourner droite 500ms
        demarrerDroite(1180);
        break;
      case 5:
      default:
        etatRobot = ETAT_ARRET;
        stopMoteurs();
        break;
    }
  }

  // ===== 2. LIRE COMMANDES SÉRIE (RPi) =====
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      if (commandBuffer.length() > 0) {
        traiterCommande(commandBuffer);
        commandBuffer = "";
      }
    } else {
      commandBuffer += c;
    }
  }

  // ===== 3. MACHINE À ÉTATS — GESTION CONTINUE =====
  unsigned long elapsed = millis() - moveStartTime;

  switch (etatRobot) {

    // --- AVANCE : vérification obstacle en continu ---
    case ETAT_AVANCE: {
      float cpt1 = mesurerDistance(TRIG1, ECHO1);
      float cpt3 = mesurerDistance(TRIG3, ECHO3);

      if (cpt1 < OBSTACLE_DISTANCE || cpt3 < OBSTACLE_DISTANCE) {
        // Obstacle détecté → lancer évitement
        lancerEvitement(cpt1, cpt3);
        break;
      }

      // Fin de durée (mouvement série) → arrêt
      if (!commandeBT_continue && elapsed >= moveDuration) {
        stopMoteurs();
        etatRobot = ETAT_ARRET;
        Serial.println("Mouvement terminé");
      }
      break;
    }

    // --- RECULE : vérification obstacle arrière en continu ---
    case ETAT_RECULE: {
      float cpt2 = mesurerDistance(TRIG2, ECHO2);

      if (cpt2 < OBSTACLE_DISTANCE) {
        stopMoteurs();
        etatRobot = ETAT_ARRET;
        Serial.println("!! Obstacle arrière → arrêt");
        break;
      }

      if (!commandeBT_continue && elapsed >= moveDuration) {
        stopMoteurs();
        etatRobot = ETAT_ARRET;
        Serial.println("Mouvement terminé");
      }
      break;
    }

    // --- ROTATION GAUCHE/DROITE (durée fixe) ---
    case ETAT_GAUCHE:
    case ETAT_DROITE: {
      if (elapsed >= moveDuration) {
        stopMoteurs();
        etatRobot = ETAT_ARRET;
        Serial.println("Rotation terminée");
      }
      break;
    }

    // ===== SÉQUENCE D'ÉVITEMENT (non-bloquante) =====

    // Phase 1 : reculer 300ms
    case ETAT_EVITEMENT_RECUL: {
      if (elapsed >= moveDuration) {
        stopMoteurs();
        moveStartTime = millis();
        moveDuration = 150; // Pause 150ms
        etatRobot = ETAT_EVITEMENT_PAUSE;
      }
      break;
    }

    // Phase 2 : pause courte
    case ETAT_EVITEMENT_PAUSE: {
      if (elapsed >= moveDuration) {
        // Tourner dans la direction choisie
        moveStartTime = millis();
        moveDuration = 750; // Durée de rotation
        etatRobot = ETAT_EVITEMENT_TOURNE;
        if (directionEvitement > 0) {
          droite();
          Serial.println("  Évitement → tourne droite");
        } else {
          gauche();
          Serial.println("  Évitement → tourne gauche");
        }
      }
      break;
    }

    // Phase 3 : tourner 750ms
    case ETAT_EVITEMENT_TOURNE: {
      if (elapsed >= moveDuration) {
        stopMoteurs();
        // Vérifier si la voie est libre avant de reprendre
        float cpt1 = mesurerDistance(TRIG1, ECHO1);
        float cpt3 = mesurerDistance(TRIG3, ECHO3);

        if (cpt1 > OBSTACLE_DISTANCE && cpt3 > OBSTACLE_DISTANCE) {
          // Voie libre → reprendre l'avance (en continu si BT)
          Serial.println("  Voie libre → reprise avance");
          demarrerAvance(moveDuration, commandeBT_continue);
        } else {
          // Toujours bloqué → nouvel essai dans l'autre sens
          Serial.println("  Toujours bloqué → nouvel essai");
          directionEvitement = -directionEvitement; // Inverser direction
          lancerEvitement(cpt1, cpt3);
        }
      }
      break;
    }

    case ETAT_ARRET:
    default:
      break;
  }

  // ===== 4. ENVOI PÉRIODIQUE DES CAPTEURS VERS LE RPi =====
  unsigned long now = millis();
  if (now - lastSensorSend >= SENSOR_SEND_INTERVAL) {
    lastSensorSend = now;
    float d1 = mesurerDistance(TRIG1, ECHO1);
    float d2 = mesurerDistance(TRIG2, ECHO2);
    float d3 = mesurerDistance(TRIG3, ECHO3);
    // Format : SENSORS:<avant_g>:<arriere>:<avant_d>
    Serial.print("SENSORS:");
    Serial.print(d1, 1);
    Serial.print(":");
    Serial.print(d2, 1);
    Serial.print(":");
    Serial.println(d3, 1);
  }

  // Petite pause pour ne pas saturer les capteurs
  delay(50);
}
