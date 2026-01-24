/*================================================================

Groupe : 5

Code écrit par : Antonin GERAIN 

Fonction du code :
    - Initialisation des fonctions de l'interface logiciel.

================================================================*/
#ifndef IHM_H
#define IHM_H

/* Menus */
void ecran_accueil();
void menu_principal();
void menu_administrateur();

/* Menus utilisateur */
void menu_utilisateur();

/* Pilotage robot */
void menu_pilotage_robot();
void choix_environnement();
void pilotage_manuel();
void pilotage_vocal();
void pilotage_textuel();

/* Traitement image */
void menu_traitement_image();

/* Sécurité */
int connexion_admin();

#endif