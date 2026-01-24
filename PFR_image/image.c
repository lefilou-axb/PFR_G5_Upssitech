#include <stdio.h>
#include <stdlib.h>
#include "image.h"

/*============================================================================*/
/*  Auteur        : Adrien Nosel                                               */
/*  Date création : 13/12/2025                                                 */
/*                                                                            */
/*  Description   : Implémentation des fonctions de chargement,               */
/*                  quantification et écriture d'images RGB.                 */
/*============================================================================*/

/* ========================================================= */
/*                  CHARGEMENT DE L'IMAGE                    */
/* ========================================================= */

int charger_image(const char *nom_fichier, ImageRGB *image)
{
    int nb_canaux, taille, i;
    FILE *fichier = fopen(nom_fichier, "r");
    if (!fichier) return -1;
    fscanf(fichier, "%d %d %d",
               &image->nb_lignes,
               &image->nb_colonnes,
               &nb_canaux);

    if (nb_canaux != 3) {
        fclose(fichier);
        return -1;
    }

    taille = image->nb_lignes * image->nb_colonnes;
    image->R = malloc(taille * sizeof(unsigned char));
    image->G = malloc(taille * sizeof(unsigned char));
    image->B = malloc(taille * sizeof(unsigned char));

    if (!image->R || !image->G || !image->B) {
        fclose(fichier);
        return -1;
    }

    /* Lecture de la matrice Rouge */
    for (i = 0; i < taille; i++)
        fscanf(fichier, "%hhu", &image->R[i]);

    /* Lecture de la matrice Verte */
    for (i = 0; i < taille; i++)
        fscanf(fichier, "%hhu", &image->G[i]);

    /* Lecture de la matrice Bleue */
    for (i = 0; i < taille; i++)
        fscanf(fichier, "%hhu", &image->B[i]);

    fclose(fichier);
    return 0;
}

/* Libération de la mémoire */
void liberer_image(ImageRGB *image)
{
    free(image->R);
    free(image->G);
    free(image->B);
}

/* ========================================================= */
/*                    QUANTIFICATION                         */
/* ========================================================= */

/* Garde uniquement les n bits de poids forts */
unsigned int quantifier_valeur(unsigned char valeur, int nb_bits)
{
    return valeur >> (8 - nb_bits);
}

/*
 Construction du nombre RRGGBB sur 6 bits
 */
unsigned int quantifier_pixel(unsigned char r,
                              unsigned char g,
                              unsigned char b,
                              int nb_bits)
{
    unsigned int qR = quantifier_valeur(r, nb_bits);
    unsigned int qG = quantifier_valeur(g, nb_bits);
    unsigned int qB = quantifier_valeur(b, nb_bits);

    return (qR << (2 * nb_bits)) |
           (qG << (nb_bits)) |
           (qB);
}

/* ========================================================= */
/*               ÉCRITURE DE L'HISTOGRAMME                   */
/* ========================================================= */

unsigned int *quantifier_image(const ImageRGB *image, int nb_bits)
{
    int i;
    int taille = image->nb_lignes * image->nb_colonnes;
    unsigned int *image_quantifiee = malloc(taille * sizeof(unsigned int));
    if (!image_quantifiee) return NULL;

    for (i = 0; i < taille; i++) {
        image_quantifiee[i] = quantifier_pixel(image->R[i],
                                               image->G[i],
                                               image->B[i],
                                               nb_bits);
    }

    return image_quantifiee;
}

int ecrire_image_quantifiee(const char *nom_fichier,
                            const unsigned int *donnees,
                            int nb_lignes,
                            int nb_colonnes)
{
    int i;
    FILE *fichier = fopen(nom_fichier, "w");
    if (!fichier) return -1;

    fprintf(fichier, "%d %d 1\n", nb_lignes, nb_colonnes);

    for (i = 0; i < nb_lignes * nb_colonnes; i++) {
        fprintf(fichier, "%u ", donnees[i]);

        /* Retour à la ligne à chaque fin de ligne */
        if ((i + 1) % nb_colonnes == 0)
            fprintf(fichier, "\n");
    }

    fclose(fichier);
    return 0;
}
