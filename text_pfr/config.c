#include <stdio.h>
#include <string.h>
#include "config.h"

/* Variables globales */
char current_language[8] = "fr";
lexicon_entry_t lexicon[MAX_LEXICON];
int lexicon_size = 0;

/*
 * Charge uniquement un lexique
 */
int load_lexicon(const char *filename) {

    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Erreur ouverture lexique");
        return 0;
    }

    char line[128];
    lexicon_size = 0;

    while (fgets(line, sizeof(line), file)) {

        if (line[0] == '#' || line[0] == '\n')
            continue;

        if (sscanf(line, "%31[^;];%d;%31s",
                   lexicon[lexicon_size].text,
                   (int *)&lexicon[lexicon_size].type,
                   lexicon[lexicon_size].value) == 3) {

            lexicon_size++;
        }
    }

    fclose(file);
    return 1;
}

/*
 * Charge la configuration globale (langue + lexique)
 */
int load_configuration(void) {

    FILE *file = fopen("config_lang.txt", "r");
    if (file) {
        fscanf(file, "language=%7s", current_language);
        fclose(file);
    }

    if (strcmp(current_language, "en") == 0)
        return load_lexicon("lexique_en.txt");

    return load_lexicon("lexique_fr.txt");
}
