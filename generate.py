# Copyright (c) Gyorgy Wyatt Muntean 2017
# This python module serves as the only executable module in the repo.
# This is the top-level script which writes all verilog modules, testbenches,
# noise sources, and wrappers. 
# See the README for a detailed description of runtime arguments and flags.

import argparse
import os
import sc_gen
import tb_gen

REP_OPTIONS = ["uni", "bi"]  # types of supported stochastic representations

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
      default='', help='Name sufix for all generated modules'
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
      '-p', dest='rep', action='store', type=str, required=False,
      default='uni', help='Type of stochastic representation, options are Uni or Bi'
   )
   parser.add_argument(
      '-alaghi', dest='alaghi', action='store', type=bool, required=False,
      default=False, help='Switches to alaghi adders instead of conventional sc adders'
   )
   args = parser.parse_args()
   args.rep = str.lower( args.rep )

   # Argument validation
   if ( args.rep not in REP_OPTIONS ):
      print( "Usage: -p [uni|bi]" )
      exit()
   if ( not os.path.isdir( args.dest_dir ) ):
      print( "ERROR: dst={} is not a valid path".format( args.dest_dir ) )
      exit()

   return args


# Script entry point function
if __name__ == '__main__':
   args = cli()
   print( "Generating Modules..." )
   sc_gen.generate( args )
   print( "done!" )
   print( "Generating Testbenches..." )
   tb_gen.generate( args )
   print( "done!" )
