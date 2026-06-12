#include <string.h>
#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include "lexer.h"
#include "config.h"

/*
 * Met un token en minuscules afin de rendre
 * l'analyse insensible à la casse (AVANCE = avance)
 */
static void to_lowercase(char *token) {
    for (int i = 0; token[i]; i++)
        token[i] = (char)tolower((unsigned char)token[i]);
}

/*
 * Supprime la ponctuation finale d'un token
 * (virgule, point, point-virgule, deux-points)
 */
static void clean_token(char *token) {
    int len = strlen(token);
     while (len > 0 &&
          (token[len - 1] == ',' ||
           token[len - 1] == '.' ||
           token[len - 1] == ';' ||
           token[len - 1] == ':')) {
        token[--len] = '\0';
    }

    /* Suppression du symbole degré UTF-8 */
    char *deg = strstr(token, "°");
    if (deg)
        *deg = '\0';
}


/*
 * Vérifie si une chaîne est composée uniquement de chiffres
 */
static int is_number(const char *s) {
    for (int i = 0; s[i]; i++)
        if (!isdigit((unsigned char)s[i]))
            return 0;
    return 1;
}

/*
 * Vérifie si le token est de la forme :
 * nombre + unité collée (ex: 3m, 50cm, 45deg)
 */
static int is_number_with_unit(const char *token) {
    int i = 0;
    while (isdigit((unsigned char)token[i])) i++;
    return (i > 0 && token[i] != '\0');
}

/*
 * Analyse lexicale :
 * - découpe la phrase
 * - normalise la casse
 * - nettoie la ponctuation
 * - reconnaît les mots via le lexique
 * - reconnaît les nombres (séparés ou collés)
 * - normalise les distances en mètres
 */
int lexical_analysis(char *sentence, word_t words[]) {

    int count = 0;
    char *token = strtok(sentence, " \n");

    while (token && count < MAX_WORDS) {

        /* Normalisations de base */
        to_lowercase(token);
        clean_token(token);

        int found = 0;

        /* Recherche directe dans le lexique */
        for (int i = 0; i < lexicon_size && !found; i++) {
            if (strcmp(token, lexicon[i].text) == 0) {
                words[count].type = lexicon[i].type;
                strcpy(words[count].value, lexicon[i].value);
                found = 1;
            }
        }

        /* Nombre + unité collée (ex: 3m, 50cm, 45deg) */
        if (!found && is_number_with_unit(token)) {

            int i = 0;
            while (isdigit((unsigned char)token[i])) i++;

            double value = atof(token);
            char unit[16];
            strcpy(unit, &token[i]);

            /*
             * Normalisation des unités :
             * - distances en mètres
             * - angles en degrés (pas convertis ici)
             */
            if (strcmp(unit, "cm") == 0)
                value /= 100.0;

            words[count].type = WORD_NUMBER;
            sprintf(words[count].value, "%.2f", value);
            count++;

            token = strtok(NULL, " \n");
            continue;
        }

        /* Nombre seul (ou nombre + unité séparée) */
        if (!found && is_number(token)) {

            double value = atof(token);
            char *next = strtok(NULL, " \n");

            if (next) {
                to_lowercase(next);
                clean_token(next);

                /* Si une unité suit, on la traite */
                if (strcmp(next, "cm") == 0)
                    value /= 100.0;
                else if (strcmp(next, "m") != 0)
                    token = next;
            }

            words[count].type = WORD_NUMBER;
            sprintf(words[count].value, "%.2f", value);
            count++;

            token = strtok(NULL, " \n");
            continue;
        }

        /* Mot inconnu (conservé pour debug ou extensions) */
        if (!found) {
            words[count].type = WORD_UNKNOWN;
            strcpy(words[count].value, token);
        }

        count++;
        token = strtok(NULL, " \n");
    }

    return count;
}
