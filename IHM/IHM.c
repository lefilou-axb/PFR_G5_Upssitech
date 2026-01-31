/* =================================================================
Groupe  : 5
Auteur  : Antonin GERAIN 

Description :   Interface utilisateur et administrateur du logiciel 
                embarqué
                Intégration des autres modules (Traitement d'image, 
                Requêtes textes, Requêtes vocales et Simulation).
=================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "configuration.h"

/* ================= FONCTIONS REQUÊTES TEXTES ================= */
#include "text_request.h"
#include "config.h"
#include "IHM.h"
#include "lang.h"
#include "lexer.h"
#include "interpreter.h"
/* ============================================================= */

/* ================= FONCTIONS TRAITEMENT IMAGES ================= */
#include "image.h"
#include "module_test.h"
/* =============================================================== */

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

    while (!saisir_choix(&choix) || choix > 3) {
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
        default: 
            break;
    }
}

void menu_utilisateur()
{
    int choix = 0;

    printf("\n%s\n\n", txt("TITLE_USER"));
    printf("\n%s\n", txt("USER_MENU"));
    printf("> ");
        
    while (!saisir_choix(&choix) || choix > 3) {
        printf("%s\n", txt("INPUT_ERROR"));
        printf("> ");
    }

    switch (choix) {
        case 1:
            choix_environnement();
            break;
        case 2:
            menu_traitement_image();
            break;
        default:
            break;
    }
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

    printf("\n%s\n", txt("ENV_SELECT"));
    printf(" %d\n", env);

    menu_pilotage_robot();
}

void menu_pilotage_robot()
{
    int choix = 0;

    printf("\n%s\n\n ", txt("TITLE_PILOTING"));
    printf("\n%s\n", txt("PILOT_MENU"));
    printf("> ");

    while (!saisir_choix(&choix) || choix > 3) {
        printf("%s\n", txt("INPUT_ERROR"));
        printf("> ");
    }

    switch (choix) {
        case 1:
            pilotage_vocal();
            break;
        case 2:
            pilotage_textuel();
            break;
        case 3:
            menu_utilisateur();
        default: break;
        }
}

void pilotage_manuel()
{
    printf("\n%s\n\n", txt("TITLE_MANUAL"));
    printf("\n%s\n", txt("MANUAL_MSG"));
}

void pilotage_vocal()
{
    printf("\n%s\n\n", txt("TITLE_VOICE"));
    system("python3 ../Module_vocal/Module_vocal.py");
    
    // --- Lire le résultat de la transcription ---
    /*FILE *file = fopen("vocal_res.txt", "r");
    if (file != NULL) {
        char buffer[256];
        if (fgets(buffer, sizeof(buffer), file)) {
            printf("Traitement de la commande vocale : %s\n", buffer);
            
            word_t words[255];
            command_t cmds[255];

            int w = lexical_analysis(buffer, words);
            int c = interpret_words(words, w, cmds);
            
            // Export pour la simulation
            export_commands("commands.txt", cmds, c); 
            
            printf("\n%s\n", txt("REQUEST_EXP"));
            
            // Lancer la simulation (comme dans pilotage_textuel)
            system("python3 ../Simulation/readCmd.py");
        }
        fclose(file);
        remove("vocal_res.txt"); // Nettoyage
    } else {
        printf("Erreur : Impossible de récupérer la commande vocale.\n");
    }*/

    /*if (handle_text_request()) {
        system("python3 ../Simulation/readCmd.py");
    }*/

    menu_pilotage_robot();
}

void pilotage_textuel()
{
    printf("\n%s\n\n", txt("TITLE_TEXTUAL"));
    printf("\n%s\n", txt("REQUEST_MSG"));

    if (handle_text_request()) {
        system("python3 ../Simulation/readCmd.py");
    }
    
    menu_pilotage_robot();

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

    int bit, vmin, vmax;
    int nb_bits;  /*nombre de bits de quantification (1 à 8)*/
    /*------------------------------------------------------------*/

    printf("\n%s\n\n", txt("TITLE_IMAGE"));
    printf("\n%s\n", txt("IMAGE_MENU"));

    if (!lire_config("config/image.txt", &bit, &vmin, &vmax, &nb_bits)) {
        printf("%s\n", txt("READ_ERROR"));
    } 
    else {
        printf("%s\n", txt("CONFIG_VALUE_RETRIEVED"));
        printf("> %d\n", nb_bits);
    }

    quantification_IMG300(num, nb, nb_bits);
    txt_to_image(num, nb, nb_bits);

    printf("\n%s\n", txt("IMAGE_END"));

    menu_utilisateur();
}


/* ================= ADMINISTRATEUR ================= */
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
    menu_principal();

    int c;
    while ((c = getchar()) != '\n' && c != EOF);

    return 0;
}

void menu_administrateur()
{
    int choix = 0;

    printf("\n%s\n\n", txt("TITLE_ADMIN"));
    printf("\n%s\n", txt("ADMIN_MENU"));
    printf("> ");

    while (!saisir_choix(&choix) || choix > 2) {
        printf("%s\n", txt("INPUT_ERROR"));
        printf("> ");
    }

    switch (choix) {
        case 1: 
            menu_config_image();
            break;
        case 2: 
            break;
    }
}

/* ================= CONFIGURATIONS ================= */
void menu_config_image()
{
    int choix = 0;

    int bit, vmin, vmax, mod;

    printf("\n%s\n\n", txt("TITLE_CONFIG_IMG"));
    printf("%s\n", txt("CONFIG_MENU"));
    printf("> ");

    while (!saisir_choix(&choix) || choix < 1 || choix > 2) {
        printf("%s\n", txt("INPUT_ERROR"));
        printf("> ");
    }

    switch (choix) {

        case 1:
            /* Lecture du fichier */
            if (!lire_config("config/image.txt", &bit, &vmin, &vmax, &mod)) {
                printf("%s\n", txt("READ_ERROR"));
                break;
            }

            /* Affichage */
            afficher_config(bit, vmin, vmax, mod);

            /* Saisie nouvelle valeur */
            if (!saisir_valeur(&mod)) {
                printf("%s\n", txt("WRITE_ERROR"));
                break;
            }

            /* Vérification simple */
            if (mod < vmin || mod > vmax) {
                printf("%s [%d ; %d]\n", txt("CONFIG_OUT_OF_RANGE"), vmin, vmax);
                break;
            }

            /* Écriture */
            if (!ecrire_config("config/image.txt", bit, vmin, vmax, mod)) {
                printf("%s\n", txt("CONFIG_WRITE_ERROR"));
                break;
            }

            printf("%s\n", txt("CONFIG_UPDATE_SUCCESS"));
            break;
        case 2:
            break;
    }

    menu_administrateur();

}
