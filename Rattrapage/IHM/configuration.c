#include <stdio.h>
#include <string.h>
#include "configuration.h"
#include "lang.h"

/* Lit la configuration depuis le fichier */
int lire_config(const char *nom_fichier, int *bit, int *vmin, int *vmax, int *mod)
{
    FILE *f = fopen(nom_fichier, "r");
    if (f == NULL)
        return 0;

    if (fscanf(f, "%d %d %d %d", bit, vmin, vmax, mod) != 4) {
        fclose(f);
        return 0;
    }

    fclose(f);
    return 1;
}

/* Écrit la configuration dans le fichier */
int ecrire_config(const char *nom_fichier,
                  int bit, int vmin, int vmax, int mod)
{
    FILE *f = fopen(nom_fichier, "w");
    if (f == NULL)
        return 0;

    fprintf(f, "%d %d %d %d\n", bit, vmin, vmax, mod);
    fclose(f);
    return 1;
}

/* Demande à l'utilisateur une nouvelle valeur */
int saisir_valeur(int *mod)
{
    printf("%s\n", txt("NEW_VALUE"));
    printf("> ");
    if (scanf("%d", mod) != 1)
        return 0;
    
    return 1;
}

/* Affiche la configuration */
void afficher_config(int bit, int vmin, int vmax, int mod)
{
    printf("%s\n", txt("CONFIG_ACT"));
    printf("  bit  = %d\n", bit);
    printf("  min  = %d\n", vmin);
    printf("  max  = %d\n", vmax);
    printf("  mod  = %d\n", mod);
}
