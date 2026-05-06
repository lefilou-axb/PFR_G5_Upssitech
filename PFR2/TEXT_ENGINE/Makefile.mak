# =========================
# Compilation des fichiers objets
# =========================

main.o: main.c config.h lexer.h interpreter.h text_request.h types.h
	gcc -Wall -Wextra -c main.c

config.o: config.c config.h types.h
	gcc -Wall -Wextra -c config.c

lexer.o: lexer.c lexer.h config.h types.h
	gcc -Wall -Wextra -c lexer.c

interpreter.o: interpreter.c interpreter.h types.h
	gcc -Wall -Wextra -c interpreter.c

text_request.o: text_request.c text_request.h lexer.h interpreter.h config.h types.h
	gcc -Wall -Wextra -c text_request.c


# =========================
# Édition de liens
# =========================

pfr_text.out: main.o config.o lexer.o interpreter.o text_request.o
	gcc main.o config.o lexer.o interpreter.o text_request.o -o pfr_text.out


# =========================
# Nettoyage
# =========================

clean:
	rm -f *.o pfr_text
