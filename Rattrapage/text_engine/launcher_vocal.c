/* launcher_vocal.c */
/* Ce code sert uniquement à lancer la fonction de traitement texte */

// On déclare la fonction externe (présente dans text_request.c)
void handle_text_request(void); 

int main() {
    // On appelle la fonction. 
    // Elle va attendre du texte sur l'entrée standard (stdin).
    handle_text_request(); 
    return 0;
}