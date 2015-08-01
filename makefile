SRCDIR := ./src
all:
	$(SRCDIR)/compile.py

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
