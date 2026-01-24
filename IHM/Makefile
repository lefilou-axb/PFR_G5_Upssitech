CFLAGS = -Wall -Wextra -std=c99 -I.. -I../text_engine -I../PFR_image

TEXT_ENGINE = ../text_engine
TEXT_IMAGE = ../PFR_image
TEXT_OBJS = $(TEXT_ENGINE)/config.o $(TEXT_ENGINE)/lexer.o $(TEXT_ENGINE)/interpreter.o $(TEXT_ENGINE)/text_request.o $(TEXT_IMAGE)/image.o $(TEXT_IMAGE)/module_test.o

all: IHM_main.out

IHM_main.out: IHM_main.o IHM.o ../lang.o $(TEXT_OBJS)
	gcc -o $@ IHM_main.o IHM.o ../lang.o $(TEXT_OBJS) $(CFLAGS)

../lang.o: ../lang.c ../lang.h
	gcc $(CFLAGS) -c ../lang.c -o ../lang.o

IHM_main.o: IHM.h IHM_main.c
	gcc $(CFLAGS) -c IHM_main.c -o IHM_main.o

IHM.o: IHM.c IHM.h
	gcc $(CFLAGS) -c IHM.c -o IHM.o

clean:
	rm -f *.o IHM_main.out IMG_300_Q/*.txt IMG_300_AC/*.pgm

