/* ==============================================================
Groupe  : 5
Auteur  : Antonin GERAIN 

Description :   Initialisation des fonctions de l'interface 
                logiciel.
                Description des fonctions écrites dans IHM.c
=============================================================== */
#ifndef IHM_H
#define IHM_H

/* ==================== MENUS ==================== */
/* Ces fonctions permettent d'afficher les         */
/* différents menus avec une sélection via une     */
/* saisie au clavier des chiffres associés.        */
/* =============================================== */
void ecran_accueil();
void menu_principal();

/* ==================== MENU UTILISATEUR ==================== */
/* Affiche les choix des fonctionnalitées du robot :          */
/*      -   Pilotage                                          */
/*      -   Traitement d'image                                */
/* ========================================================== */
void menu_utilisateur();

/* ==================== PILOTAGE ROBOT ==================== */
/* Choix de l'environnement où le robot se déplace.         */
/* Appel des différentes fonctions du pilotage du robot :   */
/*      -   Pilotage avec requêtes vocales                  */
/*      -   Pilotage avec requêtes textuelles               */
/* ======================================================== */
void menu_pilotage_robot();
void choix_environnement();
void pilotage_manuel();
void pilotage_vocal();
void pilotage_textuel();

/* ==================== TRAITEMENT IMAGES ==================== */
/* Appel des fonctions gérant le traitement des images.        */
/* =========================================================== */
void menu_traitement_image();

/* ==================== ADMINISTRATEUR ==================== */
/* Gestion de la connexion au menu administrateur avec un   */
/* identifiant (admin) et un mot de passe (robot).          */
/* L'utilisateur possède de 3 essaies pour se connecter.    */
/* Au bout de 3 échecs, un décompte de 30 secondes se lance.*/
/* ======================================================== */
int connexion_admin();
void menu_administrateur();

void menu_config_image();

#endif