#include <stdio.h>
#include <stdlib.h>
#include "image.h"
#include "module_test.h"

/*============================================================================*/
/*  Auteur        : Adrien Nosel                                               */
/*  Date création : 13/12/2025                                                 */
/*                                                                            */
/*  Description   : Implémentation des fonctions de test pour la               */
/*                  quantification d'images IMG300 et la génération           */
/*                  d'images visualisables à partir de données                */
/*                  quantifiées.                                              */
/*============================================================================*/


/* ========================================================= */
/*              QUANTIFICATION DE IMG300                     */
/* ========================================================= */

int quantification_IMG300(int num, int nb, int nb_bits)
{
    int i;
    char path_entree[100];
    char path_sortie[100];
    ImageRGB image;
    
    for (i = 0; i < nb; i++) {
        
        sprintf(path_entree,"IMG_300/IMG_%d.txt", num);
        sprintf(path_sortie,"IMG_300_Q/IMG_%d_q.txt", num);
        const char *fichier_entree  = path_entree;
        const char *fichier_sortie  = path_sortie;
        
        /* Chargement de l'image */
        if (charger_image(fichier_entree, &image) != 0) {
            return 1;
        }
        
        /* Quantification de l'image */
        unsigned int *image_quantifiee = quantifier_image(&image, nb_bits);
        
        if (!image_quantifiee) {
            liberer_image(&image);
            return 1;
        }
        
        /* Écriture du résultat */
        ecrire_image_quantifiee(fichier_sortie,
                                image_quantifiee,
                                image.nb_lignes,
                                image.nb_colonnes);
        
        /* Libération mémoire */
        free(image_quantifiee);
        liberer_image(&image);
        
        num++;
    }
    
    return 0;
}



/* ========================================================= */
/*               AFFICHAGE DANS IMG300_AC                    */
/* ========================================================= */

void txt_to_image(int num, int nb, int nb_bits)
{
    int i, j, k;
    char path_entree[100];
    char path_sortie[100];
    int largeur = 300;
    int hauteur = 300;
    int max_val = (1 << nb_bits) - 1;
    int a, b, c;
    float facteur = 255.0f / max_val;
    
    for (i = 0; i < nb; i++) {
        
        sprintf(path_entree,"IMG_300_Q/IMG_%d_q.txt", num);
        sprintf(path_sortie,"IMG_300_AC/IMG_%d_ac.pgm", num);
        const char *fichier_entree  = path_entree;
        const char *fichier_sortie  = path_sortie;
        
        FILE *entree = fopen(fichier_entree, "r");
        FILE *sortie = fopen(fichier_sortie, "w");
        
        fprintf(sortie, "P3\n%d %d\n255\n", largeur, hauteur);
        fscanf(entree, "%d%d%d", &a ,&b, &c);
        
        for (j = 0; j < hauteur; j++)
        {
            for (k = 0; k < largeur; k++)
            {
                int p;
                fscanf(entree, "%d", &p);
                
                int r = (p >> (2*nb_bits)) & ((1<<nb_bits)-1);
                int g = (p >> (nb_bits)) & ((1<<nb_bits)-1);
                int b = p & ((1<<nb_bits)-1);
                
                int rf = (int)(r * facteur);
                int gf = (int)(g * facteur);
                int bf = (int)(b * facteur);
                
                fprintf(sortie, "%d %d %d ", rf, gf, bf);
            }
            fprintf(sortie, "\n");
        }
        
        fclose(entree);
        fclose(sortie);
        
        num++;
    }
}

