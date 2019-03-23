.PHONY: black flake8

all:

flake8:
	flake8

black:
	black -l 100 .
