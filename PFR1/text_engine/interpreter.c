#include <string.h>
#include <stdlib.h>
#include "interpreter.h"

/*
 * Rôle :
 * - transformer les mots issus du lexer en commandes abstraites (type turtle)
 */

int interpret_words(word_t words[], int n, command_t cmds[])
{
    int command_count = 0;

    for (int i = 0; i < n; i++) {

        /* =====================================================
         * 1️⃣ MOTS SPÉCIAUX
         * ===================================================== */
        if (words[i].type == WORD_SPECIAL) {

            /* ---------- DEMI-TOUR ---------- */
            if (!strcmp(words[i].value, "U_TURN")) {
                strcpy(cmds[command_count].action, "left");
                cmds[command_count].value = 180.0;
                cmds[command_count].target[0] = '\0';
                command_count++;
            }

            /* ---------- REVIENS ---------- */
            if (!strcmp(words[i].value, "COME_BACK")) {
                strcpy(cmds[command_count].action, "left");
                cmds[command_count].value = 180.0;
                cmds[command_count].target[0] = '\0';
                command_count++;

                strcpy(cmds[command_count].action, "forward");
                cmds[command_count].value = 1.0;
                cmds[command_count].target[0] = '\0';
                command_count++;
            }

            /* ---------- ZIGZAG (contextuel) ---------- */
            if (!strcmp(words[i].value, "ZIGZAG")) {

                char move_action[16] = "forward";
                double step = 10.0;
                double angle = 45.0;

                /* Recherche du dernier déplacement AVANT zigzag */
                for (int k = i - 1; k >= 0; k--) {
                    if (words[k].type == WORD_ACTION) {

                        if (!strcmp(words[k].value, "forward") ||
                            !strcmp(words[k].value, "backward")) {

                            strcpy(move_action, words[k].value);
                            step = 1.0;

                            for (int m = k + 1; m < i; m++) {
                                if (words[m].type == WORD_NUMBER)
                                    step = atof(words[m].value);
                            }
                            break;
                        }
                    }
                }

                /* Motif zigzag */
                strcpy(cmds[command_count].action, move_action);
                cmds[command_count].value = step;
                cmds[command_count].target[0] = '\0';
                command_count++;

                strcpy(cmds[command_count].action, "left");
                cmds[command_count].value = angle;
                cmds[command_count].target[0] = '\0';
                command_count++;

                strcpy(cmds[command_count].action, move_action);
                cmds[command_count].value = step;
                cmds[command_count].target[0] = '\0';
                command_count++;

                strcpy(cmds[command_count].action, "right");
                cmds[command_count].value = angle;
                cmds[command_count].target[0] = '\0';
                command_count++;
            }

            /* ---------- CERCLE ---------- */
            if (!strcmp(words[i].value, "CIRCLE")) {

                for (int k = 0; k < 8; k++) {
                    strcpy(cmds[command_count].action, "forward");
                    cmds[command_count].value = 0.5;
                    cmds[command_count].target[0] = '\0';
                    command_count++;

                    strcpy(cmds[command_count].action, "left");
                    cmds[command_count].value = 45.0;
                    cmds[command_count].target[0] = '\0';
                    command_count++;
                }
            }
        }

        /* =====================================================
         * 2️⃣ ACTIONS CLASSIQUES
         * ===================================================== */
        if (words[i].type == WORD_ACTION) {

            int neg_before = 0;
            int alternative_found = 0;
            int has_zigzag = 0;

            /* Négation avant l'action */
            for (int k = 0; k < i; k++) {
                if (words[k].type == WORD_NEGATION)
                    neg_before = 1;
            }

            
            for (int k = i + 1; k < n && words[k].type != WORD_ACTION; k++) {
                if (words[k].type == WORD_SPECIAL && strcmp(words[k].value, "ZIGZAG") == 0) {
                    has_zigzag = 1;
                }
            }

            /* Alternative après (mais / et / puis) */
            for (int k = i + 1; k < n; k++) {
                if (words[k].type == WORD_LINK) {
                    for (int m = k + 1; m < n && words[m].type != WORD_ACTION; m++) {
                        if (words[m].type == WORD_DIRECTION ||
                            words[m].type == WORD_NUMBER ||
                            words[m].type == WORD_OBJECT)
                            alternative_found = 1;
                    }
                }
            }

            if (neg_before && !alternative_found)
                goto skip_action;

            if (has_zigzag &&
                (!strcmp(words[i].value, "forward") ||
                 !strcmp(words[i].value, "backward")))
                continue;
            
            command_t *cmd = &cmds[command_count];

            cmd->value = 0.0;
            cmd->target[0] = '\0';

            /* Valeurs par défaut */
            if (!strcmp(words[i].value, "forward") ||
                !strcmp(words[i].value, "backward")) {

                strcpy(cmd->action, words[i].value);
                cmd->value = 1.0;
            }

            if (!strcmp(words[i].value, "turn")) {
                strcpy(cmd->action, "left");
                cmd->value = 90.0;
            }

            if (!strcmp(words[i].value, "goto")) {

                strcpy(cmd->action, words[i].value);
            }

            /* Paramètres */
            int negate_next = 0;

            for (int j = i + 1; j < n && words[j].type != WORD_ACTION; j++) {

                if (words[j].type == WORD_NEGATION)
                    negate_next = 1;

                if (words[j].type == WORD_NUMBER) {
                    if (!negate_next)
                        cmd->value = atof(words[j].value);
                    negate_next = 0;
                }

                if (words[j].type == WORD_DIRECTION) {
                    if (!negate_next) {
                        if (!strcmp(words[j].value, "LEFT"))
                            strcpy(cmd->action, "left");
                        if (!strcmp(words[j].value, "RIGHT"))
                            strcpy(cmd->action, "right");
                    }
                    negate_next = 0;
                }

                if (words[j].type == WORD_OBJECT) {
                    strcpy(cmd->target, words[j].value);
                    if (j + 1 < n && words[j + 1].type == WORD_COLOR) {
                        strcat(cmd->target, "_");
                        strcat(cmd->target, words[j + 1].value);
                    }
                }
            }

            command_count++;

        skip_action:
            ;
        }
    }

    return command_count;
}
