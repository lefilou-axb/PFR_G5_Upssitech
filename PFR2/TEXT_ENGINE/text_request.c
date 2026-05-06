/* =================================================================
Groupe  : 5
Auteur  : Ny Aina RAHARITSIFA 

Description :   Récupération des instructions données par 
                l'utilisateur pour les transférer vers les fonctions
                de l'interprétateur et la simulation.
=================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include "lexer.h"
#include "interpreter.h"
#include "config.h"
#include "text_request.h"

#define COMMANDS_FILE "/mnt/d/PFR/PFR_G5_Upssitech/PFR2/TEXT_ENGINE/commands.txt"

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

    export_commands(COMMANDS_FILE, cmds, c);
    printf("\nCommandes exportées dans commands.txt\n");
    return 1;
}

/* ---------------------------------------------------------------
 * handle_vocal_request : lit la transcription depuis le fichier
 * écrit par Module_vocal.py, puis applique le même pipeline que
 * handle_text_request (lexer → interpréteur → export).
 *
 * filepath : chemin vers vocal_res.txt
 *
 * Retourne 1 si des commandes ont été générées, 0 sinon.
 * ------------------------------------------------------------- */
int handle_vocal_request(const char *filepath)
{
    char input[256];
    word_t words[MAX_WORDS];
    command_t cmds[MAX_COMMANDS];

    FILE *file = fopen(filepath, "r");
    if (!file) {
        printf("Erreur : impossible de lire la transcription vocale (%s).\n", filepath);
        return 0;
    }

    if (!fgets(input, sizeof(input), file)) {
        fclose(file);
        printf("Erreur : fichier de transcription vide.\n");
        return 0;
    }
    fclose(file);

    /* Suppression du fichier temporaire pour éviter de rejouer
     * une ancienne transcription lors de la prochaine session  */
    remove(filepath);

    printf("Commande vocale transcrite : %s\n", input);

    int w = lexical_analysis(input, words);
    int c = interpret_words(words, w, cmds);

    if (c == 0) {
        printf("Aucune commande reconnue dans la transcription.\n");
        return 0;
    }

    printf("\nCommandes générées :\n");
    for (int i = 0; i < c; i++) {
        if (cmds[i].target[0])
            printf("- %s %s\n", cmds[i].action, cmds[i].target);
        else
            printf("- %s %.2f\n", cmds[i].action, cmds[i].value);
    }

    export_commands(COMMANDS_FILE, cmds, c);
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
