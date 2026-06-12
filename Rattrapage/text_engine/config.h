#ifndef CONFIG_H
#define CONFIG_H

#include "types.h"

/* Tailles maximales */
#define MAX_WORDS 64
#define MAX_COMMANDS 32
#define MAX_LEXICON 128

/* Entrée du lexique */
typedef struct {
    char text[32];
    word_type_t type;
    char value[32];
} lexicon_entry_t;

/* Lexique global */
extern lexicon_entry_t lexicon[MAX_LEXICON];
extern int lexicon_size;

/* Langue courante */
//extern char current_language[8];

/* Fonctions */
int load_configuration(int langue);
int load_lexicon(const char *filename);

#endif
