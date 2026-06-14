#ifndef MODULE_TEST_H
#define MODULE_TEST_H

/*============================================================================*/
/*  Auteur        : Adrien Nosel                                               */
/*  Date création : 18/12/2025                                                 */
/*                                                                            */
/*  Description   : Déclarations des fonctions de test pour la                */
/*                  quantification d'images IMG300 et la conversion           */
/*                  de fichiers texte vers des images visualisables.          */
/*============================================================================*/


/*----------------------------------------------------------------------------*/
/* Quantification d'un ensemble d'images IMG300                               */
/*                                                                            */
/* @param num       Numéro de la première image à traiter                     */
/* @param nb        Nombre d'images à traiter                                 */
/* @param nb_bits   Nombre de bits utilisés pour la quantification            */
/*                                                                            */
/* @return 0 en cas de succès, valeur non nulle en cas d'erreur               */
/*----------------------------------------------------------------------------*/
int quantification_IMG300(int num, int nb, int nb_bits);


/*----------------------------------------------------------------------------*/
/* Conversion des fichiers texte quantifiés en images affichables             */
/*                                                                            */
/* @param num       Numéro de la première image à traiter                     */
/* @param nb        Nombre d'images à traiter                                 */
/* @param nb_bits   Nombre de bits utilisés pour la quantification            */
/*----------------------------------------------------------------------------*/
void txt_to_image(int num, int nb, int nb_bits);

#endif /* MODULE_TEST_H */
