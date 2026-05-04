#include <stdio.h>
#include "config.h"
#include "text_request.h"

int main(void) {
    if (!load_configuration()) {
        printf("Erreur chargement configuration\n");
        return 1;
    }
    printf("Langue chargée : %s\n", current_language);
    commander_robot();
    return 0;
}