# Copyright (c) Gyorgy Wyatt Muntean 2017

# arguments to pass to make clean target
DONTCLEAN = -maxdepth 1 -not -name "Makefile" -not -name README -not -name "sc_gen.py" -not -name "srcs" -not -name ".git" -not -name "." -not -name ".."

# Main target
all : run

# run the script with no arguments (sort of useless)
run :
	python sc_gen.py

# delete everything not in DONTCLEAN args
clean :
	find . $(DONTCLEAN) | xargs rm -rf
