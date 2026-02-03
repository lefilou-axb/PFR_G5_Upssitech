#include <stdio.h>
#include <string.h>
#include "lexer.h"
#include "interpreter.h"
#include "config.h"
#include "lang.h"

/*
 * Exporte les commandes pour la simulation
 * Format : action,valeur|cible
 */
void export_commands(const char *filename, command_t cmds[], int n) {

    FILE *file = fopen(filename, "w");
    if (!file) return;
    //fprintf(file,"%s\n","commande,valeur");
    for (int i = 0; i < n; i++) {
        if (cmds[i].target[0])
            fprintf(file, "%s %s\n", cmds[i].action, cmds[i].target);
        else
            fprintf(file, "%s %.2f\n", cmds[i].action, cmds[i].value);
    }

    fclose(file);
}

int handle_text_request(void)
{
    char input[256];
    word_t words[MAX_WORDS];
    command_t cmds[MAX_COMMANDS];

    printf("> ");

    if (!fgets(input, sizeof(input), stdin))
        return 1;  // on continue par défaut

    input[strcspn(input, "\n")] = 0; // suppression du \n

    /* condition de sortie */
    if (strcmp(input, "1") == 0)
        return 0;

    int w = lexical_analysis(input, words);
    int c = interpret_words(words, w, cmds);

    /* Aucun résultat exploitable */
    if (c == 0) {
        printf("\n%s\n", txt("CMD_ERROR"));
        return 0;
    }
    
    printf("\n%s\n", txt("REQUEST_CMD"));
    for (int i = 0; i < c; i++) {
        if (cmds[i].target[0])
            printf("- %s %s\n", cmds[i].action, cmds[i].target);
        else
            printf("- %s %.2f\n", cmds[i].action, cmds[i].value);
    }

    export_commands("commands.txt", cmds, c);
    printf("\n%s\n", txt("REQUEST_EXP"));
    
    return 1;
}