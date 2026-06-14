#include <AFMotor.h>

// Capteur 1 (avant1)
#define TRIG1 22
#define ECHO1 24

// Capteur 2 (arrière)
#define TRIG2 48
#define ECHO2 50

// Capteur 3 (avant2)
#define TRIG3 41
#define ECHO3 38

AF_DCMotor m1(1);
AF_DCMotor m2(2);
AF_DCMotor m3(3);
AF_DCMotor m4(4);

int c;

// ==================== AJOUTS (VERSION 2) ====================

// --------- CALIBRATION ----------
#define DISTANCE_RATIO 0.0008
#define ANGLE_RATIO 0.12
#define OBSTACLE_DISTANCE 30.0

// --------- VARIABLES SUPPLÉMENTAIRES ----------
unsigned long moveStartTime = 0;
unsigned long moveDuration = 0;
bool isMoving = false;
int currentMoveType = 0;
String commandBuffer = "";
int motorSpeed = 200;
int bluetoothCommand = 0;

// --------- VITESSE MOTEURS ----------
void setMotorSpeed(int speed) {
  motorSpeed = speed;
  m1.setSpeed(speed);
  m2.setSpeed(speed);
  m3.setSpeed(speed);
  m4.setSpeed(speed);
}

// --------- MOUVEMENTS AVEC DISTANCE / ANGLE ----------
void avancerDistance(float distanceMetres) {
  moveDuration = (unsigned long)(distanceMetres / DISTANCE_RATIO);
  moveStartTime = millis();
  isMoving = true;
  currentMoveType = 1;

  Serial.println(">> Avance distance calibrée");
  avancer();
}

void reculerDistance(float distanceMetres) {
  moveDuration = (unsigned long)(distanceMetres / DISTANCE_RATIO);
  moveStartTime = millis();
  isMoving = true;
  currentMoveType = 2;

  Serial.println(">> Recule distance calibrée");
  reculer();
}

void tournerAngle(float angleDegres) {
  moveDuration = (unsigned long)(abs(angleDegres) / ANGLE_RATIO);
  moveStartTime = millis();
  isMoving = true;

  if (angleDegres > 0) {
    currentMoveType = 4;
    droite();
  } else {
    currentMoveType = 3;
    gauche();
  }
}

// --------- VÉRIFICATION OBSTACLES ----------
bool verifierObstacles() {
  float cpt1 = mesurerDistance(TRIG1, ECHO1);
  float cpt2 = mesurerDistance(TRIG2, ECHO2);
  float cpt3 = mesurerDistance(TRIG3, ECHO3);

  if (currentMoveType == 1) {
    if (cpt1 < OBSTACLE_DISTANCE || cpt3 < OBSTACLE_DISTANCE) {
      return false;
    }
  }

  if (currentMoveType == 2) {
    if (cpt2 < OBSTACLE_DISTANCE) {
      return false;
    }
  }

  return true;
}

// --------- TRAITEMENT DE COMMANDES TEXTE ----------
void traiterCommande(String commande) {
  commande.trim();

  int espaceIndex = commande.indexOf(' ');
  if (espaceIndex == -1) return;

  String cmd = commande.substring(0, espaceIndex);
  float valeur = commande.substring(espaceIndex + 1).toFloat();

  if (cmd == "forward") {
    avancerDistance(valeur);
  }
  else if (cmd == "backward") {
    reculerDistance(valeur);
  }
  else if (cmd == "right") {
    tournerAngle(valeur);
  }
  else if (cmd == "left") {
    tournerAngle(-valeur);
  }
  else if (cmd == "stop") {
    stopMoteurs();
  }
}

// FONTIONS MOTEURS

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

//  MESURE DISTANCE
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

//  SETUP
void setup() {
  Serial.begin(115200);
  Serial1.begin(115200); // Bluetooth

  m1.setSpeed(200);
  m2.setSpeed(200);
  m3.setSpeed(200);
  m4.setSpeed(200);

  stopMoteurs();

  pinMode(TRIG1, OUTPUT);
  pinMode(ECHO1, INPUT);

  pinMode(TRIG2, OUTPUT);
  pinMode(ECHO2, INPUT);

  pinMode(TRIG3, OUTPUT);
  pinMode(ECHO3, INPUT);
}

//  PROGRAMME PRINCIPAL
void loop() {

  // Lecture capteurs
  float cpt1 = mesurerDistance(TRIG1, ECHO1);
  float cpt2 = mesurerDistance(TRIG2, ECHO2);
  float cpt3 = mesurerDistance(TRIG3, ECHO3);

  Serial.print("Capteur 1 : ");
  Serial.print(cpt1);
  Serial.println(" cm");

  Serial.print("Capteur 2 : ");
  Serial.print(cpt2);
  Serial.println(" cm");

  Serial.print("Capteur 3 : ");
  Serial.print(cpt3);
  Serial.println(" cm");

  Serial.println("-------------------");


  if (Serial1.available() > 0) {
    c = Serial1.read();

    Serial.print("Commande recue : ");
    Serial.println(c);

  }

  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    Serial.print("Echo: ");
    Serial.println(data);
  }
  
  switch (c) {

    case 1: // Avancer
    if (cpt1 > 40.0 && cpt3 > 40.0) {
      avancer();
    }
    else {
      stopMoteurs();
      delay(200);

      // Reculer
      if (cpt2 >= 40.0) {
        reculer();
        delay(400);
        stopMoteurs();
        delay(200);
      }

      // Choix de direction
      if (cpt1 > cpt3) {
        droite();   // plus d’espace à droite
      } else {
        gauche();   // plus d’espace à gauche
      }

      delay(750);
      stopMoteurs();
    }

    break;

    case 2: // Reculer
      if (cpt2 >= 40.0) {
        reculer();
      } else {
        stopMoteurs();
      }
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
}