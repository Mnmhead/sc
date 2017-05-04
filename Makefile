# Copyright (c) Gyorgy Wyatt Muntean 2017

# arguments to pass to make clean target
DONTCLEAN = -maxdepth 1 -not -name "Makefile" -not -name README -not -name "sc_gen.py" -not -name "srcs" -not -name ".git" -not -name "." -not -name ".." -not -name "TODO.txt" -not -name "tb_gen.py" -not -name "common.py" -not -name "generate.py" -not -name "srcs_gen.py"

# Main target
all : run

# run the script with no arguments (sort of useless)
run :
	python generate.py

# delete everything not in DONTCLEAN args
clean :
	find . $(DONTCLEAN) | xargs rm -rf
