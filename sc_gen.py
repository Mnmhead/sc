# Copyright (c) Gyorgy Wyatt Muntean 2017

import argparse
from time import gmtime, strftime
import math
import os

REP_OPTIONS = ["uni", "bi"]

# Generates a matrix multiply module in the stochastic domain. 
# Opens and writes to a file.
# The contents of the file are specified by the users input.
def generate_modules( args ):
   M = args.batch_size
   N = args.input_size
   O = args.output_size

   # if a module name is supplied, concatenate module names
   mat_mult_name = "sc_matrix_mult"
   dp_name = "sc_dot_product"
   nadder_name = "sc_nadder"
   if args.module_name is not "":
      mat_mult_name += "_" + args.module_name
      dp_name += "_" + args.module_name
      nadder_name += "_" + args.module_name
   mat_mult_name += ".v"
   dp_name += ".v"
   nadder_name += ".v"   

   # write the matrix multiply module
   with open( os.path.join( args.dest_dir, mat_mult_name ), 'w' ) as f: 
      write_matrix_module( f, mat_mult_name, M, N, O )

   # write the dot_product module
   with open( os.path.join( args.dest_dir, dp_name ), 'w' ) as f:
      write_dot_prod_module( f, dp_name, N )

   # write the nadder module
   with open( os.path.join( args.dest_dir, nadder_name), 'w' ) as f:
      write_nadder_module( f, nadder_name, N )

   print( "Done!" )

#   
#
#
def write_matrix_module( f, module_name, batch, inpt, outpt ):
   # compute the log base 2 of the input, 
   # this is how many select streams are required
   select_width = int(math.log( inpt, 2 ))

   # write the header comment
   write_header_mat_mult( f )

   write_line( f, "module " + module_name + "(" )
   write_line( f, "clk,", 1 )
   write_line( f, "rst,", 1 )
   write_line( f, "inputStreams,", 1 )
   write_line( f, "weightStreams,", 1 )
   write_line( f, "sel,", 1 )
   write_line( f, "outputStreams,", 1 )
   write_line( f, "outputWriteEn", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter BATCH_SIZE = 4, // M", 1 )
   write_line( f, "parameter INPUT_FEATURES = 4, // N", 1 )
   write_line( f, "parameter OUTPUT_FEATURES = 4 // O", 1 )
   write_line( f, "parameter SELECT_WIDTH = " + str(select_width), 1 )
   write_line( f, "" )
   write_line( f, "// inputs and outputs", 1 )
   write_line( f, "input                                      ilk;", 1 )
   write_line( f, "input                                      rst;", 1 )
   write_line( f, "input [BATCH_SIZE*INPUT_FEATURES-1:0]      inputStreams;", 1 )
   write_line( f, "input [OUTPUT_FEATURES*INPUT_FEATURES-1:0] weightStreams;", 1 )
   write_line( f, "input [SELECT_WIDTH-1:0]                 sel;", 1 )
   write_line( f, "output [BATCH_SIZE*OUTPUT_FEATURES-1:0]    outputStreams;", 1 )
   write_line( f, "output                                     outputWriteEn;", 1 )
   write_line( f, "" )
   write_line( f, "generate", 1 )
   write_line( f, "for( i = 0; i < BATCH_SIZE; i = i + 1) begin", 2 )
   write_line( f, "for( j = 0; j < OUTPUT_FEATURES; j = j + 1) begin : dot_prod_loop", 3 )
   write_line( f, "sc_dot_product (.clk(clk),", 4 )
   write_line( f, "                .rst(rst),", 4 )
   write_line( f, "                .data(inputStreams[i*INPUT_FEATURES +: INPUT_FEATURES]),", 4 )
   write_line( f, "                .weights(weightStreams[j*INPUT_FEATURES +: INPUT_FEATURES]),", 4 )
   write_line( f, "                .sel(sel),", 4 )
   write_line( f, "                .result(outputStreams[(i*OUTPUT_FEATURES)+j]));", 4 )
   write_line( f, "end", 3 )
   write_line( f, "end", 2 )
   write_line( f, "endgenerate", 1 )
   write_line( f, "" )
   write_line( f, "// later we will incorporate this signal", 1 )
   write_line( f, "assign outputWriteEn = 1;", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // sc_matrix_mult" )

   return

#
#
# 
def write_dot_prod_module( f, module_name, length ):
   # compute number of select streams
   select_width = int( math.log( length, 2 ) )
   
   # write the header comment
   write_header_dot_prod( f )

   write_line( f, "module " + module_name + "(" )
   write_line( f, "clk,", 1 )
   write_line( f, "rst,", 1 )
   write_line( f, "data,", 1 )
   write_line( f, "weights,", 1 )
   write_line( f, "sel,", 1 )
   write_line( f, "result", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter LENGTH = " + str(length), 1 )
   write_line( f, "parameter SELECT_WIDTH = " + str(select_width), 1 )
   write_line( f, "" )
   write_line( f, "// inputs and outputs", 1 )
   write_line( f, "input                    clk;", 1 )
   write_line( f, "input                    rst;", 1 )
   write_line( f, "input [LENGTH-1:0]       data;", 1 )
   write_line( f, "input [LENGTH-1:0]       weights;", 1 )
   write_line( f, "input [SELECT_WIDTH-1:0] sel;", 1 )
   write_line( f, "output                   result;", 1 )
   write_line( f, "" ) 
   write_line( f, "// multipication modules, for element wise multiplication of data and weights", 1 )
   write_line( f, "genvar i;", 1 )
   write_line( f, "wire [LENGTH-1:0] mult_out;", 1 )
   write_line( f, "generate", 1 )
   write_line( f, "for( i = 0; i < LENGTH; i = i + 1) begin : mult", 2 )
   write_line( f, "sc_multiplier(.x(data[i]), .y(weights[i]), .res(mult_out[i]));", 3 )
   write_line( f, "end", 2 )
   write_line( f, "endgenerate", 1 )
   write_line( f, "" )
   write_line( f, "// direct multiplication output to an intermediate register", 1 )
   write_line( f, "reg [LENGTH-1:0] product_streams;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "product_streams <= mult_out;", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "// add all element-wise products", 1 )
   write_line( f, "sc_nadder #(LENGTH) (.x(product_streams), .sel(sel), .out(result));", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // sc_dot_product" )

   return

#
#
#
def write_nadder_module( f, module_name, n ):
   # compute number of select streams needed 
   select_width = int(math.log( n, 2 ))

   # write the header comment
   write_header_nadder( f )
   
   write_line( f, "module " + module_name + "(" )
   write_line( f, "x,", 1 )
   write_line( f, "sel,", 1 )
   write_line( f, "out", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter INPUT_STREAMS = " + str(n), 1 )
   write_line( f, "parameter SELECT_WIDTH = " + str(select_width), 1 )
   write_line( f, "" )
   write_line( f, "input [INPUT_STREAMS-1:0] x;", 1 )
   write_line( f, "input [SELECT_WIDTH-1:0]  sel;", 1 )
   write_line( f, "output                    out;", 1 )
   write_line( f, "" )
   write_line( f, "assign out = x[sel];", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // sc_nadder" )

   return

   
# Writes the header comment for the sc_matrix_mult module.
# This comment nincludes a timestamp of when the file was genertaed, in GMT.
def write_header_mat_mult( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: This moudle represents matrix multiply in the stochastic domain." )
   write_line( f, "// ihe inputs to this module are two flattened matrices A and B," )
   write_line( f, "// where A has dimensions MxN and B has dimensions NxO." )
   write_line( f, "// The input matrix B however should be the flattened form of the transpose of B." )
   write_line( f, "// This results in a matrix C with dimensions MxO." )
   write_line( f, "//" )
   write_line( f, "// For more information on stochastic computing:" )
   write_line( f, "// https://en.wikipedia.org/wiki/Stochastic_computing" )
   write_line( f, "//" )
   write_line( f, "// Requirement: parameter INPUT_FEATURES, N, must be a power of 2." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )
   
   return

# Writes the header comment for the sc_dot_product module.
# The file written to is the parameter, f.
def write_header_dot_prod( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a dot product of two vectors in the stochastic domain." )
   write_line( f, "// For more information on stochastic computing:" )
   write_line( f, "// https://en.wikipedia.org/wiki/Stochastic_computing" )
   write_line( f, "//" )
   write_line( f, "// Requirement: The inputs, 'sel', must be stochastic bitstreams where probability of" )
   write_line( f, "// a 1 or 0 is equally 0.5." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )
   
   return

# Writes the header comment for the sc_nadder module.
# The file written to is the parameter, f.
def write_header_nadder( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a multi-input adder in the stochastic domain." )
   write_line( f, "// For more information on stochastic computing: https://en.wikipedia.org/wiki/Stochastic_computing" )
   write_line( f, "//" )
   write_line( f, "// Requirements:" )
   write_line( f, "// The number of input streams must be a power of 2. The input 'sel' must" )
   write_line( f, "// be the concatenation of log2(INPUT_STREAMS) number of un-correlated stochastic streams" )
   write_line( f, "// (each with value=0.5)." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

   return


#-----------Testbench Generation------------#
# Function which opens and writes testbench files for the verilog modules
# generated (and specified by the users input arguments).
def generate_testbenches( args ):
   pass


#---------Helper functions-----------#
# Helper function to write to file, f.
# Writes string to file f with numTabs number of tabs before
# the string and a newline character after the string.
def write_line( f, string, numTabs=0 ):
   tab = ""
   for i in range(0,numTabs):
      tab += "   "
   f.write( tab + string + "\n" )

# Helper function.
# Returns true if num is a power of 2, false otherwise.
def power_of_2( num ):
   return num != 0 and ((num & (num - 1)) == 0)

# Helper function to get the time and date in GMT
def get_time():
   return strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " GMT"

#----------Argument Handler---------#
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

   # Argument validation
   if ( str.lower(args.rep) not in REP_OPTIONS ):
      print( "Usage: -p [uni|bi]" )
      exit()
   if ( not os.path.isdir( args.dest_dir ) ):
      print( "ERROR: dst={} is not a valid path".format( args.dest_dir ) )
      exit()
   if ( not power_of_2( args.input_size ) ):
      print( "Usage: -is input must be a power of 2" )
      exit()
  
   return args 


# Script entry point function
if __name__ == '__main__':
   args = cli()
   print( "Generating Modules..." )
   generate_modules( args )
   print( "done!" )
   print( "Generating Testbenches..." )
   generate_testbenches( args ) 
   print( "done!" )
