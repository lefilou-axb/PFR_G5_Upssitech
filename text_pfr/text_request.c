#include <stdio.h>
#include "lexer.h"
#include "interpreter.h"
#include "config.h"

/*
 * Exporte les commandes pour la simulation
 * Format : action,valeur|cible
 */
static void export_commands(const char *filename,
                            command_t cmds[],
                            int n) {

    FILE *file = fopen(filename, "w");
    if (!file) return;
    fprintf(file,"%s\n","commande valeur");
    for (int i = 0; i < n; i++) {
        if (cmds[i].target[0])
            fprintf(file, "%s %s\n", cmds[i].action, cmds[i].target);
        else
            fprintf(file, "%s %.2f\n", cmds[i].action, cmds[i].value);
    }

    fclose(file);
}

void handle_text_request(void) {

    char input[256];
    word_t words[MAX_WORDS];
    command_t cmds[MAX_COMMANDS];

    printf("Veuillez entrer une commande texte :\n> ");
    fgets(input, sizeof(input), stdin);

    int w = lexical_analysis(input, words);
    int c = interpret_words(words, w, cmds);

    printf("\nCommandes générées :\n");
    for (int i = 0; i < c; i++) {
        if (cmds[i].target[0])
            printf("- %s %s\n", cmds[i].action, cmds[i].target);
        else
            printf("- %s %.2f\n", cmds[i].action, cmds[i].value);
    }

    export_commands("commands.txt", cmds, c);
    printf("\nCommandes exportées dans commands.txt\n");
}
