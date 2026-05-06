#include <string.h>
#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include "lexer.h"
#include "config.h"

/* =======================
 * Normalisation des tokens
 * ======================= */

static void to_lowercase(char *token)
{
    for (int i = 0; token[i]; i++)
        token[i] = (char)tolower((unsigned char)token[i]);
}

static void clean_token(char *token)
{
    int len = strlen(token);
    while (len > 0 &&
          (token[len - 1] == ',' ||
           token[len - 1] == '.' ||
           token[len - 1] == ';' ||
           token[len - 1] == ':')) {
        token[--len] = '\0';
    }

    /* suppression du symbole degré */
    char *deg = strstr(token, "°");
    if (deg)
        *deg = '\0';
}

/* =======================
 * Tests numériques
 * ======================= */

static int is_number(const char *s)
{
    for (int i = 0; s[i]; i++)
        if (!isdigit((unsigned char)s[i]))
            return 0;
    return 1;
}

static int is_number_with_unit(const char *token)
{
    int i = 0;
    while (isdigit((unsigned char)token[i])) i++;
    return (i > 0 && token[i] != '\0');
}

/* =======================
 * Analyse lexicale
 * ======================= */

int lexical_analysis(char *sentence, word_t words[])
{
    int count = 0;
    char *token = strtok(sentence, " \n");

    while (token && count < MAX_WORDS) {

        to_lowercase(token);
        clean_token(token);

        int found = 0;

        /* 1️⃣ Recherche dans le lexique */
        for (int i = 0; i < lexicon_size && !found; i++) {
            if (strcmp(token, lexicon[i].text) == 0) {
                words[count].type = lexicon[i].type;
                strcpy(words[count].value, lexicon[i].value);
                found = 1;
            }
        }

        /* 2️⃣ Nombre + unité collée */
        if (!found && is_number_with_unit(token)) {

            int i = 0;
            while (isdigit((unsigned char)token[i])) i++;

            double value = atof(token);
            char unit[16];
            strcpy(unit, &token[i]);

            /* unité collée → normalisation */
            if (strcmp(unit, "cm") == 0)
                value /= 100.0;

            words[count].type = WORD_NUMBER;
            sprintf(words[count].value, "%.2f", value);
            count++;

            token = strtok(NULL, " \n");
            continue;
        }

        /* 3️⃣ Nombre + unité séparée */
        if (!found && is_number(token)) {

            double value = atof(token);
            char *next = strtok(NULL, " \n");

            int unit_found = 0;

            if (next) {
                to_lowercase(next);
                clean_token(next);

                /* recherche de l'unité dans le lexique */
                for (int i = 0; i < lexicon_size; i++) {
                    if (strcmp(next, lexicon[i].text) == 0 &&
                        lexicon[i].type == WORD_UNIT) {

                        if (strcmp(lexicon[i].value, "cm") == 0)
                            value /= 100.0;

                        unit_found = 1;
                        break;
                    }
                }
            }

            words[count].type = WORD_NUMBER;
            sprintf(words[count].value, "%.2f", value);
            count++;

            if (!unit_found)
                token = next;
            else
                token = strtok(NULL, " \n");

            continue;
        }

        /* 4️⃣ Mot inconnu */
        if (!found) {
            words[count].type = WORD_UNKNOWN;
            strcpy(words[count].value, token);
        }

        count++;
        token = strtok(NULL, " \n");
    }

    return count;
}
