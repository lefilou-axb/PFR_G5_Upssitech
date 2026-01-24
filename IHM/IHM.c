/*================================================================

Groupe : 5

Code écrit par : Antonin GERAIN 

Fonction du code : 
    - Interface utilisateur et administrateur du logiciel embarqué
    - Intégration des autres modules (Traitement d'image, Requêtes 
        textes, Requêtes vocales et Simulation).

================================================================*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "text_request.h"
#include "config.h"
#include "IHM.h"
#include "lang.h"

#include "image.h"
#include "module_test.h"

/* ================= MENUS ================= */

void ecran_accueil()
{
    printf("\n========================================\n\n");
    printf("\n%s\n\n", txt("WELCOME"));
}

void menu_principal()
{
    int choix = 0;
    printf("\n%s\n\n", txt("TITLE_HOME"));
    printf("%s\n", txt("MENU_MAIN"));
    printf("> ");

    while (!saisir_choix(&choix)) {
        printf("%s\n", txt("INPUT_ERROR"));
        printf("> ");
    }

    switch (choix) {
        case 1: 
            menu_utilisateur(); 
            break;
        case 2:
            if (connexion_admin())
                menu_administrateur();
            break;
        case 3:
            printf("\n========================================\n\n");
            printf("%s\n", txt("EXIT_MSG"));
            exit(EXIT_SUCCESS);
        default: break;
    }
}

void menu_utilisateur()
{
    int choix = 0;
    do {
        printf("\n%s\n\n", txt("TITLE_USER"));
        printf("\n%s\n", txt("USER_MENU"));
        printf("> ");
        
        while (!saisir_choix(&choix)) {
            printf("%s\n", txt("INPUT_ERROR"));
            printf("> ");
        }

        switch (choix) {
            case 1:
                menu_pilotage_robot();
                break;
            case 2:
                menu_traitement_image();
                break;
            default: break;
        }
    } while (choix != 3);
}

/* ================= PILOTAGE ================= */

void choix_environnement()
{
    int env;
    printf("\n%s\n ", txt("ENV_CHOICE"));
    printf("> ");
    
    while (!saisir_choix(&env)) {
        printf("%s\n", txt("INPUT_ERROR"));
        printf("> ");
    }

    printf("Environnement %d selectionne\n", env);
}

void menu_pilotage_robot()
{
    int choix = 0;

    printf("\n%s\n\n ", txt("TITLE_PILOTING"));
    choix_environnement();

    do {
        printf("\n========================================\n\n");
        printf("\n%s\n", txt("PILOT_MENU"));
        printf("> ");

        while (!saisir_choix(&choix)) {
            printf("%s\n", txt("INPUT_ERROR"));
            printf("> ");
        }

        switch (choix) {
            case 1:
                pilotage_manuel();
                break;
            case 2:
                pilotage_vocal();
                break;
            case 3:
                pilotage_textuel();
                break;
            default: break;
        }
    } while (choix != 4);
}

void pilotage_manuel()
{
    printf("\n%s\n\n", txt("TITLE_MANUAL"));
    printf("\n%s\n", txt("MANUAL_MSG"));
}

void pilotage_vocal()
{
    printf("\n%s\n\n", txt("TITLE_VOICE"));
    //printf("\n%s\n", txt("VOCAL_MSG"));

    system("python3 ../Module_vocal/Module_vocal.py");
}

void pilotage_textuel()
{
    printf("\n%s\n\n", txt("TITLE_TEXTUAL"));

    printf("\n%s\n", txt("REQUEST_MSG"));

    /*while (1) {
        if (!handle_text_request())
            break;
    }*/

    handle_text_request();

    system("python3 ../Simulation/readCmd.py");
}


/* ================= IMAGE ================= */

void menu_traitement_image()
{
    /*--------------------------DECLRATION--------------------------*/
    /* Paramètres */
    int num = 5389;   /*indice de la première image à quantifier (5389)*/
    int nb = 20;      /*nombre d'images à quantifier (20 dans le dossier fourni)*/
    /*les deux première variables sont des constantes car c'est toujours je même
     fichier avec toujours les mêmes images dedans et toujours le même nombre
     d'images. Mais par la suite nous aurons peutêtre besoin d'avoir ces parametres
     hors des fonctions.*/
    int nb_bits = 2;  /*nombre de bits de quantification (1 à 8)*/
    /*------------------------------------------------------------*/

    printf("\n%s\n\n", txt("TITLE_IMAGE"));
    printf("\n%s\n", txt("IMAGE_MENU"));

    quantification_IMG300(num, nb, nb_bits);
    txt_to_image(num, nb, nb_bits);

    printf("\n%s\n", txt("IMAGE_END"));
}


/* ================= ADMIN ================= */

int connexion_admin()
{
    char id[32], mdp[32];
    int essais = 0;

    while (essais < 3) {
        printf("\n%s\n\n", txt("TITLE_LOGIN"));

        const char *msg_id  = txt("LOGIN_ID");
        const char *msg_pwd = txt("LOGIN_PWD");

        if (!msg_id || !msg_pwd) {
            printf("%s\n", txt("LANG_ERROR"));
            return 0;
        }

        printf("%s\n> ", msg_id);
        if (scanf("%31s", id) != 1)
            return 0;

        int c;
        while ((c = getchar()) != '\n' && c != EOF);

        printf("%s\n> ", msg_pwd);
        if (scanf("%31s", mdp) != 1)
            return 0;

        while ((c = getchar()) != '\n' && c != EOF);

        if (strcmp(id, "admin") == 0 && strcmp(mdp, "robot") == 0)
            return 1;

        printf("%s\n", txt("LOGIN_FAIL"));
        essais++;
    }

    printf("\n========================================\n\n");
    printf("%s\n\n", txt("LOGIN_LOCKED"));

    printf("%s\n", txt("LOGIN_COUNTDOWN"));

    for (int i = 30; i > 0; i--) {
        printf("\r %d %s ", i, txt("SECONDS"));
        fflush(stdout);
        sleep(1);
    }

    printf("\n");

    int c;
    while ((c = getchar()) != '\n' && c != EOF);

    return 0;
}



void menu_administrateur()
{
    int choix = 0;
    do {
        printf("\n%s\n\n", txt("TITLE_ADMIN"));
        printf("\n%s\n", txt("ADMIN_MENU"));
        printf("> ");

        while (!saisir_choix(&choix)) {
            printf("%s\n", txt("INPUT_ERROR"));
            printf("> ");
        }

        switch (choix) {
            case 1: 
                afficher_fichier("config/image.csv"); break;
            case 2: 
                afficher_fichier("config/requetes.csv"); break;
            default: break;
        }
        
    } while (choix != 3);
}