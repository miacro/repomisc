SHELL=/bin/bash
MAKE=make --no-print-directory

install:
	python setup.py install --user

test:
	python -m unittest discover ./repomisc/test

uninstall:
	pip uninstall repomisc

.PHONY:
	install uninstall
