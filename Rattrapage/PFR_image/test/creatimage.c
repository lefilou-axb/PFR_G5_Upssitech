#include <stdio.h>
#include <stdlib.h>


int main(void)
{
//    int couleur = 3;
//    int largeur = 300,hauteur = 300, i, j;
//    
//    if (couleur == 1){
//        FILE *sortie = fopen("IMG_rouge.pgm", "w");
//        fprintf(sortie, "P3\n%d %d\n255\n", largeur, hauteur);
//        for (i = 0; i < hauteur; i++)
//        {
//            for (j = 0; j < largeur; j++)
//            {
//                int r = 255;
//                int g = 0;
//                int b = 0;
//                fprintf(sortie, "%d %d %d ", r, g, b);
//            }
//            fprintf(sortie, "\n");
//        }
//        fclose(sortie);
//    }
//    if (couleur == 2){
//        FILE *sortie = fopen("IMG_bleue.pgm", "w");
//        fprintf(sortie, "P3\n%d %d\n255\n", largeur, hauteur);
//        for (i = 0; i < hauteur; i++)
//        {
//            for (j = 0; j < largeur; j++)
//            {
//                int r = 0;
//                int g = 0;
//                int b = 255;
//                fprintf(sortie, "%d %d %d ", r, g, b);
//            }
//            fprintf(sortie, "\n");
//        }
//        fclose(sortie);
//    }
//    if (couleur == 3){
//        FILE *sortie = fopen("IMG_jaune.pgm", "w");
//        fprintf(sortie, "P3\n%d %d\n255\n", largeur, hauteur);
//        for (i = 0; i < hauteur; i++)
//        {
//            for (j = 0; j < largeur; j++)
//            {
//                int r = 255;
//                int g = 200;
//                int b = 0;
//                fprintf(sortie, "%d %d %d ", r, g, b);
//            }
//            fprintf(sortie, "\n");
//        }
//        fclose(sortie);
//    }
    
//    
//    int couleur = 3;
//    int largeur = 300,hauteur = 300, i, j;
//    FILE *sortie1 = fopen("IMG_rouge.txt", "w");
//        
//    for (int i = 0 ; i < largeur ; i++){
//        for (int j = 0 ; j < hauteur ; j++){
//            fprintf(sortie1, "%d ", 48);
//        }
//    }
//    
//    FILE *sortie2 = fopen("IMG_bleu.txt", "w");
//        
//    for (i = 0 ; i < largeur ; i++){
//        for (j = 0 ; j < hauteur ; j++){
//            fprintf(sortie2, "%d ", 3);
//        }
//    }
    
    
    int val = 0;
    int nb_bits = 2;
    int largeur = 1 << (nb_bits*3), hauteur = 1 << (nb_bits*3), i, j;
    FILE *sortie1 = fopen("IMG_arc_en_ciel.txt","w");
    FILE *sortie2 = fopen("IMG_arc_en_ciel.pgm","w");
    
    fprintf(sortie2, "P3\n%d %d\n255\n", largeur, hauteur);
    
    for (int i = 0 ; i < largeur ; i++){
        for (int j = 0 ; j < hauteur ; j++){
            val = j;
            fprintf(sortie1, "%d", val);
            int r, g, b;
            
            r = ((val >> (2*nb_bits)) & ((1<<nb_bits)-1));
            g = ((val >> (nb_bits)) & ((1<<nb_bits)-1));
            b = (val & ((1<<nb_bits)-1));
            
            r = (int)r *(255/(2^nb_bits-1));
            g = ((int)g) *(255/(2^nb_bits-1));
            b = ((int)b) *(255/(2^nb_bits-1));
            
//            if (  (j>15) & (j<20)
//                | (j>23) & (j<28)
//                | (j>47) & (j<52)
//                | (j>55) & (j<60)){
//                /*La balle est rouge*/
//                r = 255;
//                g = 255;
//                b = 255;
//            }
//            else{
//                r = ((val >> (2*nb_bits)) & ((1<<nb_bits)-1))*(256/2^nb_bits);
//                g = ((val >> (nb_bits)) & ((1<<nb_bits)-1))*(256/2^nb_bits);
//                b = (val & ((1<<nb_bits)-1))*(256/2^nb_bits);
//            }
            
            fprintf(sortie2, "%d %d %d ", r, g, b);
        }
        fprintf(sortie1, "\n");
        fprintf(sortie2, "\n");
    }
    fclose(sortie1);
    fclose(sortie2);
    return 0;
}

