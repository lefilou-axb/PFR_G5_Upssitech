#ifndef IMAGE_H
#define IMAGE_H

/*============================================================================*/
/*  Auteur        : Adrien Nosel                                              */
/*  Date création : 13/12/2025                                                */
/*                                                                            */
/*  Description   : Définition des structures et prototypes de fonctions      */
/*                  pour la manipulation d'images RGB, leur quantification    */
/*                  et l'écriture des données quantifiées dans des fichiers.  */
/*============================================================================*/

/*----------------------------------------------------------------------------*/
/* Structure représentant une image RGB                                       */
/*                                                                            */
/* Les composantes R, G et B sont stockées séparément sous forme de tableaux  */
/* de taille nb_lignes * nb_colonnes.                                         */
/*----------------------------------------------------------------------------*/
typedef struct
{
    int nb_lignes;         /* Nombre de lignes de l'image */
    int nb_colonnes;       /* Nombre de colonnes de l'image */

    unsigned char *R;      /* Composante Rouge */
    unsigned char *G;      /* Composante Verte */
    unsigned char *B;      /* Composante Bleue */

} ImageRGB;

/*----------------------------------------------------------------------------*/
/* Chargement d'une image depuis un fichier texte                             */
/*                                                                            */
/* @param nom_fichier  Nom du fichier à charger                               */
/* @param image        Pointeur vers la structure ImageRGB à remplir          */
/*                                                                            */
/* @return 0 en cas de succès, valeur négative en cas d'erreur                */
/*----------------------------------------------------------------------------*/
int charger_image(const char *nom_fichier, ImageRGB *image);

/*----------------------------------------------------------------------------*/
/* Libération de la mémoire associée à une image                              */
/*                                                                            */
/* @param image  Pointeur vers la structure ImageRGB à libérer                */
/*----------------------------------------------------------------------------*/
void liberer_image(ImageRGB *image);

/*----------------------------------------------------------------------------*/
/* Quantification d'une valeur sur nb_bits bits de poids forts                */
/*                                                                            */
/* @param valeur   Valeur initiale sur 8 bits                                 */
/* @param nb_bits  Nombre de bits de poids forts à conserver                  */
/*                                                                            */
/* @return Valeur quantifiée                                                  */
/*----------------------------------------------------------------------------*/
unsigned int quantifier_valeur(unsigned char valeur, int nb_bits);

/*----------------------------------------------------------------------------*/
/* Quantification d'un pixel RGB                                              */
/*                                                                            */
/* @param r        Composante rouge                                           */
/* @param g        Composante verte                                           */
/* @param b        Composante bleue                                           */
/* @param nb_bits  Nombre de bits utilisés par composante                     */
/*                                                                            */
/* @return Valeur quantifiée du pixel                                         */
/*----------------------------------------------------------------------------*/
unsigned int quantifier_pixel(unsigned char r,
                              unsigned char g,
                              unsigned char b,
                              int nb_bits);

/*----------------------------------------------------------------------------*/
/* Création de la matrice quantifiée d'une image                               */
/*                                                                            */
/* @param image    Image RGB source                                           */
/* @param nb_bits  Nombre de bits utilisés par composante                      */
/*                                                                            */
/* @return Pointeur vers la matrice quantifiée (allocation dynamique)         */
/*----------------------------------------------------------------------------*/
unsigned int *quantifier_image(const ImageRGB *image, int nb_bits);

/*----------------------------------------------------------------------------*/
/* Écriture d'une image quantifiée dans un fichier texte                      */
/*                                                                            */
/* @param nom_fichier  Nom du fichier de sortie                               */
/* @param donnees      Matrice quantifiée                                     */
/* @param nb_lignes    Nombre de lignes                                        */
/* @param nb_colonnes  Nombre de colonnes                                      */
/*                                                                            */
/* @return 0 en cas de succès, valeur négative en cas d'erreur                */
/*----------------------------------------------------------------------------*/
int ecrire_image_quantifiee(const char *nom_fichier,
                            const unsigned int *donnees,
                            int nb_lignes,
                            int nb_colonnes);

#endif /* IMAGE_H */
