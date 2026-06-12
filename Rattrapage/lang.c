/*================================================================
Groupe  : 5
Auteur  : Antonin GERAIN 

Description :   Chargement et configuration des langues de 
                l'interface.
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
    printf("        CHOISISSEZ VOTRE LANGUE | CHOOSE YOUR LANGUAGE\n");
    printf("=============================================================\n\n");
    printf("1.Français\n");
    printf("2.English\n");
    printf("> ");

    while (!saisir_choix(&langue) || (langue > 2)) {
        printf("Erreur : veuillez saisir uniquement un nombre valide\n");
        printf("Error: please enter numbers only.\n");
        printf("> ");
    }
    
    return langue;
}

/* ================= CHARGEMENT DE LA LANGUE ================= */
void charger_langue(const char *fichier)
{
    FILE *f = fopen(fichier, "r");  // Ouverture du fichier
    char ligne[MAX_STR];

    /* Vérifie si le fichier existe */
    if (!f) {
        perror("Erreur chargement langue / Language loading error");
        exit(EXIT_FAILURE);
    }

    /* Parcours du fichie et stock les données dans deux tableaux */
    nb_textes = 0;
    while (fgets(ligne, MAX_STR, f)) {
        sscanf(ligne, "%[^=]=%[^\n]", textes[nb_textes].cle, textes[nb_textes].valeur); // Séparation des clefs et des valeurs
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
    return "Chaîne de caractère inconnue / Unknown string.";
}

/* ================= OUTILS ================= */
void interpreter_sauts_ligne(char *str)
{
    char temp[MAX_STR];
    int i = 0, j = 0;

    /* Boucle jusqu'à atteindre \0 */
    while (str[i]) {
        if (str[i] == '\\' && str[i+1] == 'n') {    // Détection de "\n" dans le fichier
            temp[j++] = '\n';                       // Remplacement par le caractère '\n'
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
    char buffer[32];    // stockage des instructions saisient au clavier -> 32 caractères max
    int i;

    /* Contrôle si la lecture de la saisie a fonctionnée */
    if (!fgets(buffer, sizeof(buffer), stdin))
        return 0;

    buffer[strcspn(buffer, "\n")] = 0;  // suppression du \n

    /* Vérifie si le buffer est vide */
    if (buffer[0] == '\0')
        return 0;

    /* Vérifie si le buffer ne contient que des chiffres */
    for (i = 0; buffer[i]; i++) {
        if (!isdigit((unsigned char)buffer[i]))
            return 0;
    }

    /* Convertie le buffer en valeur entière */
    *valeur = atoi(buffer);

    /* Nettoie le buffer (sécurité) */
    memset(buffer, 0, sizeof(buffer));
    
    return 1;
}