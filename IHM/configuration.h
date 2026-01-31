#ifndef CONFIG_H
#define CONFIG_H

/* Lecture de la configuration depuis un fichier
 * Retourne 1 si succès, 0 sinon */
int lire_config(const char *nom_fichier,
                int *bit, int *vmin, int *vmax, int *mod);

/* Écriture de la configuration dans un fichier
 * Retourne 1 si succès, 0 sinon */
int ecrire_config(const char *nom_fichier, int bit, int vmin, int vmax, int mod);

/* Demande à l'utilisateur une nouvelle valeur
 * Retourne 1 si succès, 0 sinon */
int saisir_valeur(int *mod);

/* Affiche la configuration */
void afficher_config(int bit, int vmin, int vmax, int mod);

#endif /* CONFIG_H */