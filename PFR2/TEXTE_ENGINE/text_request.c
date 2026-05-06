#include <stdio.h>
#include <stdlib.h>
#include "lexer.h"
#include "interpreter.h"
#include "config.h"
#include "text_request.h"

static void export_commands(const char *filename,
                            command_t cmds[],
                            int n) {
    FILE *file = fopen(filename, "w");
    if (!file) return;
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

    printf("Veuillez entrer une commande texte :\n> ");
    fgets(input, sizeof(input), stdin);

    int w = lexical_analysis(input, words);
    int c = interpret_words(words, w, cmds);

    if (c == 0) {
        return 0;
    }

    printf("\nCommandes générées :\n");
    for (int i = 0; i < c; i++) {
        if (cmds[i].target[0])
            printf("- %s %s\n", cmds[i].action, cmds[i].target);
        else
            printf("- %s %.2f\n", cmds[i].action, cmds[i].value);
    }

    export_commands("/mnt/d/PFR/PFR_G5_Upssitech/PFR2/TEXT_ENGINE/commands.txt", cmds, c);
    printf("\nCommandes exportées dans commands.txt\n");
    return 1;
}

void commander_robot(void) {
    if (handle_text_request()) {
        int ret = system("python3 /home/ny_aina/send_commands_WINDOWS.py");
        if (ret != 0) {
            fprintf(stderr, "Erreur lors de l'exécution du script Python\n");
        }
    }
}