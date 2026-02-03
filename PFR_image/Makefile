main.out: image.o module_test.o main.o
	gcc -o main.out image.o module_test.o main.o

image.o: image.c image.h
	gcc -c image.c -o image.o -W -Wall -ansi -pedantic

module_test.o: module_test.c module_test.h image.h
	gcc -c module_test.c -o module_test.o -W -Wall -ansi -pedantic

main.o: main.c module_test.h
	gcc -c main.c -o main.o -W -Wall -ansi -pedantic

clean:
	rm -rf *.o
	
clean_img:
	rm -rf IMG_300_Q/*.txt IMG_300_AC/*.pgm
