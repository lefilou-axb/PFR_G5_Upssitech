/*================================================================

Groupe : 5

Code écrit par : Antonin GERAIN 

Fonction du code :
    - Initialisation des fonctions du chargement des langues.

================================================================*/

#ifndef LANG_H
#define LANG_H
#define MAX_STR 256

/* Config langue */
int choisir_langue(void);
void charger_langue(const char *fichier);
const char *txt(const char *cle);

/* Outils */
void interpreter_sauts_ligne(char *str);
int saisir_choix(int *valeur);

/* Chargement des fichiers de langue */
void afficher_fichier(const char *chemin);

#endif