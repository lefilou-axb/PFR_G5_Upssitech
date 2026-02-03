/*================================================================
Groupe  : 5
Auteur  : Antonin GERAIN 

Description :   Initialisation des fonctions du chargement des 
                langues.
================================================================*/

#ifndef LANG_H
#define LANG_H
#define MAX_STR 256

/* ==================== CONFIGURATION DES LANGUES ==================== */
/* Choix de la langue.                                                 */
/* Importe le fichier de la langue choisie dans deux tableaux.         */
/* =================================================================== */
int choisir_langue(void);
void charger_langue(const char *fichier);

/* ==================== INTERPRÉTATION FICHIER ==================== */
/* Recherche dans les données du fichier importé la clé voulue.     */
/* Convertie la chaîne de caractère de saut de ligne en un caractère*/
/* ================================================================ */
const char *txt(const char *cle);
void interpreter_sauts_ligne(char *str);

/* ==================== CONTRÔLE DE LA SAISIE ==================== */
/* Déclenche la saisie clavier dans un buffer.                     */
/* Vérifie si la saisie est bien effectuée.                        */
/* Vérifie si le buffer est vide.                                  */
/* Vérifie que le buffer ne contient que des chiffres.             */
/* =============================================================== */
int saisir_choix(int *valeur);

#endif