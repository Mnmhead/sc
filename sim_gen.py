# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains functions to generate the core modules for
# stochastic matrix multiply. 

from common import *
import os

# Generates simulation modules for the following stochastic
# circuits: dot_product, matrix_multiply
# args, the parser arguments from generate.py
def generate( args ):
   pass

def write_dot_product_simulation( f, module_name, dimensions, rep = "uni", alaghi = False ):
   # write DIMENSION = dimensions
   # write WIDTH = precision
   # write clk, rst datas, weights
   # initialize datas and weights with random binary values
   # 
   # compute the actual result (in binary domain) possibly using vincent's code
   #
   # instantiate lfsr's with random seeds
   #
   # instantiate SNGs, pipe in noise sources
   #
   # generate a slelect stream and instantiate the dot product module
   #
   # fukkin....instantiate the sd_converter and try and get the 'last_counter' logic down...
   # finally scale the output at the end and print the final results and errors
   # with $display()
   pass

