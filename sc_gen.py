# Copyright (c) Gyorgy Wyatt Muntean 2017

import argparse
import os

REP_OPTIONS = ["uni", "bi"]

# Generates a matrix multiply module in the stochastic domain. 
# Opens and writes to a file.
# The contents of the file are specified by the users input.
def generate_module( args ):
   M = args.batch_size
   N = args.input_size
   O = args.output_size
   

# Function which opens and writes testbench files for the verilog modules
# generated (and specified by the users input arguments).
def generate_tectbench( args ):
   pass

# Command line interface specification
# 1. -dst specifies the location of the generated files
# 2. -bs, -is, and -os are the dimensions of the input matrices to the module.
# 3. -p specifies the stochastic representation type. There are two choices
#     Unipolar and Bipolar.
def cli():
   parser = argparse.ArgumentParser(
      description='Generates Stochastic Matrix Multiply Verilog Modules'
   )
   parser.add_argument(
      '-dst', dest='dest_dir', action='store', type=str, required=False,
      default=".", help='Destination directory'
   )
   parser.add_argument(
      '-name', dest='module_name', action='store', type=str, required=False,
      default='sc_matrix_mult', help='Name prefix for all generated modules'
   )
   parser.add_argument(
      '-bs', dest='batch_size', action='store', type=int, required=False,
      default=4, help='Batch size'
   )
   parser.add_argument(
      '-is', dest='input_size', action='store', type=int, required=False,
      default=4, help='Input feature size'
   )
   parser.add_argument(
      '-os', dest='output_size', action='store', type=int, required=False,
      default=4, help='Output feature size'
   )
   """
   parser.add_argument(
      '-noise', dest='noise_src', action='store', type=str, required=False,
      default="LFSR", help='Source of random noise for stochastic number generation'
   )
   parser.add_argument(
      '-len', dest='bit_stream_len', action='store', type=int, required=False,
      default=32, help='Length of the stochacstic numbers'
   )
   """
   parser.add_argument(
      '-p', dest='rep', action'store', type=str, required=False,
      default='uni', help='Type of stochastic representation, options are Uni or Bi'
   )

   # Argument validation
   if ( str.lower(args.rep) not in REP_OPTIONS ):
      print( "Usage: -p [uni|bi]" )
      exit()
   if ( not os.path.isdir( args.dest_dir ) ):
      print( "ERROR: dst={} is not a valid path".format( args.dest_dir ) )
      exit()
  
   return args 


# Script entry point function
if __name__ == '__main__':
   print "Starting...."
   args = cli()
   print "Starting gen"
   generate_module( args )
   generate_testbench( args ) 
