all: pfr_text.out

# =========================
# Compilation des fichiers objets
# =========================

main.o: main.c config.h lexer.h interpreter.h text_request.h types.h
	gcc -Wall -Wextra -c main.c -I..

config.o: config.c config.h types.h
	gcc -Wall -Wextra -c config.c -I..

lexer.o: lexer.c lexer.h config.h types.h
	gcc -Wall -Wextra -c lexer.c -I..

interpreter.o: interpreter.c interpreter.h types.h
	gcc -Wall -Wextra -c interpreter.c -I..

text_request.o: text_request.c text_request.h lexer.h interpreter.h config.h types.h
	gcc -Wall -Wextra -c text_request.c -I..
	
../lang.o: ../lang.c ../lang.h
	gcc -Wall -Wextra -I.. -c ../lang.c -o ../lang.o

# =========================
# Édition de liens
# =========================

pfr_text.out: main.o config.o lexer.o interpreter.o text_request.o ../lang.o
	gcc main.o config.o lexer.o interpreter.o text_request.o ../lang.o -o pfr_text.out -I..

# =========================
# Nettoyage
# =========================

clean:
	rm -f *.o

