/* ===============================================================
Groupe  : 5
Auteur  : Antonin GERAIN 

Description :   Programme principal de l'interface.
                Importation du fichier de la langue sélectionnée.
                Appel la fonction ecran_accueil et menu_principal.
=============================================================== */

#include <stdio.h>
#include <stdlib.h>
#include "config.h"
#include "IHM.h"
#include "lang.h"

int main()
{
    /* INITIALISATION DE LA LANGUE */
    int langue = 0;
    
    /* CHOIX DE LA LANGUE */
    while (langue == 0) {
        langue = choisir_langue();
    }

    /* CHARGEMENT DE LA LANGUE DANS L'INTERFACE */
    switch (langue) {
        case 1: 
            charger_langue("lang/fr.txt");
            break;
        case 2:
            charger_langue("lang/en.txt");
            break;
        default: 
            break;
    }

    /* CHARGEMENT DE LA LANGUE DES REQUÊTES */
    load_configuration(langue);

    /* AFFICHAGE DE L'ACCUEIL */
    ecran_accueil();

    /* AFFICHAGE DU MENU PRINCIPAL */
    while (1)

        menu_principal();

    return 0;
}
