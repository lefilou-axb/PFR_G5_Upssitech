#ifndef TYPES_H
#define TYPES_H

/*
 * Catégories de mots reconnues par le lexer.
 * Elles sont indépendantes de la langue.
 */
typedef enum {
    WORD_ACTION = 0,
    WORD_DIRECTION = 1,
    WORD_NUMBER = 2,
    WORD_UNIT = 3,
    WORD_OBJECT = 4,
    WORD_COLOR = 5,
    WORD_LINK = 6,
    WORD_SPECIAL = 7,   /* demi-tour, reviens, retourne-toi */
    WORD_NEGATION = 8,
    WORD_UNKNOWN = 9
} word_type_t;

/*
 * Mot reconnu après analyse lexicale.
 * - type : catégorie sémantique
 * - value : valeur normalisée (indépendante de la langue)
 */
typedef struct {
    word_type_t type;
    char value[32];
} word_t;

/*
 * Commande abstraite destinée à la simulation (PFR2).
 * - action : forward, backward, left, right, goto, search
 * - value  : distance (m) ou angle (°)
 * - target : objet cible (BALL_RED, CUBE_BLUE…)
 */
typedef struct {
    char action[16];
    double value;
    char target[32];
} command_t;

#endif
