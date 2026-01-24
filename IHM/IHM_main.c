/*================================================================

Groupe : 5

Code écrit par : Antonin GERAIN 

Fonction du code : 
    - Programme principal de l'interface.
    - Importation du fichier de la langue sélectionnée.
    - Appel la fonction ecran_accueil.

================================================================*/

#include <stdio.h>
#include <stdlib.h>
#include "config.h"
#include "IHM.h"
#include "lang.h"

int main()
{
    int langue = 0;

    langue = choisir_langue();

    if (langue == 1)
        charger_langue("lang/fr.txt");
    else
        charger_langue("lang/en.txt");

    load_configuration(langue);

    ecran_accueil();

    while (1)

        menu_principal();

    return 0;
}
