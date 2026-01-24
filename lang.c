/*================================================================

Groupe : 5

Code écrit par : Antonin GERAIN 

Fonction du code :
    - Chargement et configuration des langues de l'interface.

================================================================*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include "lang.h"

/* ================= VARIABLES ================= */

typedef struct {
    char cle[64];
    char valeur[MAX_STR];
} Texte;

static Texte textes[50];
static int nb_textes = 0;

/* ================= CHOIX DE LA LANGUE ================= */

int choisir_langue(void)
{
    int langue = 0;

    printf("\n=============================================================\n");
    printf(" CHOISISSEZ VOTRE LANGUE | CHOOSE YOUR LANGUAGE\n");
    printf("=============================================================\n\n");
    printf("1. Français\n");
    printf("2. English\n");
    printf("> ");

    while (!saisir_choix(&langue) || (langue != 1 && langue != 2)) {
        printf("\n%s\n", txt("INPUT_ERROR"));
        printf("> ");
    }

    return langue;
}

/* ================= CHARGEMENT DE LA LANGUE ================= */

void charger_langue(const char *fichier)
{
    FILE *f = fopen(fichier, "r");
    char ligne[MAX_STR];

    if (!f) {
        perror("Erreur chargement langue / Language loading error");
        exit(EXIT_FAILURE);
    }

    nb_textes = 0;
    while (fgets(ligne, MAX_STR, f)) {
        sscanf(ligne, "%[^=]=%[^\n]", textes[nb_textes].cle,
               textes[nb_textes].valeur);
        
        interpreter_sauts_ligne(textes[nb_textes].valeur);
        nb_textes++;
    }
    fclose(f);
}

/* ================= INTERPRETATION ================= */

const char *txt(const char *cle)
{
    for (int i = 0; i < nb_textes; i++)
        if (strcmp(textes[i].cle, cle) == 0)
            return textes[i].valeur;
    return "??";
}

/* ================= OUTILS ================= */

void interpreter_sauts_ligne(char *str)
{
    char temp[MAX_STR];
    int i = 0, j = 0;

    while (str[i]) {
        if (str[i] == '\\' && str[i+1] == 'n') {
            temp[j++] = '\n';
            i += 2;
        } else {
            temp[j++] = str[i++];
        }
    }
    temp[j] = '\0';
    strcpy(str, temp);
}

int saisir_choix(int *valeur)
{
    char buffer[32];
    int i;

    if (!fgets(buffer, sizeof(buffer), stdin))
        return 0;

    buffer[strcspn(buffer, "\n")] = 0;

    if (buffer[0] == '\0')
        return 0;

    for (i = 0; buffer[i]; i++) {
        if (!isdigit((unsigned char)buffer[i]))
            return 0;
    }

    *valeur = atoi(buffer);

    memset(buffer, 0, sizeof(buffer));
    
    return 1;
}

/* ================= CHARGEMENT DES FICHIERS DE LANGUE ================= */

void afficher_fichier(const char *chemin)
{
    FILE *f = fopen(chemin, "r");
    char ligne[MAX_STR];

    if (!f) {
        perror("Impossible d'ouvrir le fichier / Unable to open the file");
        return;
    }

    printf("\n--- %s ---\n", chemin);
    while (fgets(ligne, MAX_STR, f))
        printf("%s", ligne);
    printf("\n");

    fclose(f);
}