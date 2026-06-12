#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "config.h"
#include "lang.h"

/* Variables globales */
lexicon_entry_t lexicon[MAX_LEXICON];
int lexicon_size = 0;

/*
 * Charge uniquement un lexique
 */
int load_lexicon(const char *filename) {

    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Erreur chargement lexique / Glossary loading error");
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
int load_configuration(int langue)
{
    switch (langue) {
        case 1:
            printf("\n%s\n\n", txt("CONFIG_CHG"));
            return load_lexicon("../text_engine/lexique_fr.txt");

        case 2:
            printf("\n%s\n\n", txt("CONFIG_CHG"));
            return load_lexicon("../text_engine/lexique_en.txt");

        default:
            return 0;
    }

    
}


