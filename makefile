SRCDIR := ./src
all:
	$(SRCDIR)/compile.py

lex:
	$(SRCDIR)/lexer.py

test:
	./test.py

clean:
	rm -Rf *.pyc *.png *.txt htmlcov env

env:
	mkdir -p env 
	virtualenv env
	cd  env
	cdsource bin/activate; pip install pydot coverage

coverage:
	coverage run ./test.py
	coverage html
