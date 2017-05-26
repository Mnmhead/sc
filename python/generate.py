# Copyright (c) Gyorgy Wyatt Muntean 2017
# This python module serves as the only executable module in the repo.
# This is the top-level script which writes all verilog modules, testbenches,
# noise sources, and wrappers. 
# See the README for a detailed description of runtime arguments and flags.

import argparse
import os
import sc_gen
import tb_gen
import sim_gen

# Command line interface specification
# See README for spec description
def cli():
   parser = argparse.ArgumentParser(
      description='Generates Stochastic Matrix Multiply Verilog Modules'
   )
   parser.add_argument(
      '-dst', dest='dest_dir', action='store', type=str, required=False,
      default="gen", help='Destination directory'
   )
   """
   parser.add_argument(
      '-name', dest='suffix', action='store', type=str, required=False,
      default='', help='Name sufix for all generated modules'
   )
   """
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
      '-rep', dest='rep', action='store', type=str, required=False,
      default='uni', help='Type of stochastic representation, options are Uni or Bi'
   )
   parser.add_argument(
      '-alaghi', dest='alaghi', action='store', type=str2bool, nargs='?', required=False,
      default=False, help='Switches to alaghi adders instead of conventional sc adders'
   )
   parser.add_argument(
      '-test', dest='test', action='store', type=str2bool, nargs='?', required=False,
      default=True, help='Specifies to skip over test bench generation'
   )
   args = parser.parse_args()
   args.rep = str.lower( args.rep )
   rep_options = ["uni", "bi"]  # types of supported stochastic representations

   # Argument validation
   if ( args.rep not in rep_options ):
      print( "Usage: -p [uni|bi]" )
      exit()
   if ( args.rep is "bi" ):
      raise NotImplementedError, "[Error] Bipolar representation is not fully supported"
   if ( args.dest_dir is "gen" ):
      if ( not os.path.exists( "gen" ) ):
         os.makedirs( "gen" )
   if ( not os.path.isdir( args.dest_dir ) ):
      print( "ERROR: dst={} is not a valid path".format( args.dest_dir ) )
      exit()

   return args

# Helper function to 'translate' user input into a boolean
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# Script entry point function
if __name__ == '__main__':
   args = cli()
   print( "Generating Modules..." )
   sc_gen.generate( args )
   print( "done!" )
   if args.test:
      print( "Generating Testbenches..." )
      tb_gen.generate( args )
      print( "done!" )
   
