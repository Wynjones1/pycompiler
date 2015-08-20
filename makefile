SRCDIR := ./src

all:
	$(SRCDIR)/codegen.py
	nasm -g -f elf -l out.lst out.s
	gcc -m32 ./stdlib/malloc.c -nostdlib -c 
	ld -melf_i386 -o out out.o malloc.o

.PHONY: asm test
asm:
	nasm -g -f elf test.s
	gcc -m32 ./stdlib/malloc.c -nostdlib -c 
	ld -melf_i386 -o test test.o malloc.o
	./test

run: all
	./out

lex:
	$(SRCDIR)/lexer.py

test:
	./test.py

clean:
	rm -Rf src/*.pyc *.pyc *.png *.txt htmlcov env

env:
	mkdir -p env 
	virtualenv env
	cd  env
	cdsource bin/activate; pip install pydot coverage

coverage:
	rm -Rf .coverage htmlcov
	coverage run --branch ./test.py
	coverage html

tac:
	./src/tac.py
