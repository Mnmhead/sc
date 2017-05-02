# Copyright (c) Gyorgy Wyatt Muntean 2017

import argparse
from time import gmtime, strftime
import math
import os

REP_OPTIONS = ["uni", "bi"]  # types of supported stochastic representations 
MATRIX = "sc_matrix_mult"
DOT_PROD = "sc_dot_product"
NADDER = "sc_nadder"

#------------Module Generation----------------#
# Generates a matrix multiply module in the stochastic domain. 
# Opens and writes to a file.
# The contents of the file are specified by the users input.
def generate_modules( args ):
   M = args.batch_size
   N = args.input_size
   O = args.output_size

   # if a module name is supplied, concatenate module names
   mat_mult_name = MATRIX
   dp_name = DOT_PROD
   nadder_name = NADDER
   if args.module_name is not "":
      mat_mult_name += "_" + args.module_name
      dp_name += "_" + args.module_name
      nadder_name += "_" + args.module_name

   # write the matrix multiply module
   with open( os.path.join( args.dest_dir, mat_mult_name + ".v" ), 'w' ) as f: 
      write_matrix_module( f, mat_mult_name, M, N, O )

   # write the dot_product module
   with open( os.path.join( args.dest_dir, dp_name + ".v" ), 'w' ) as f:
      write_dot_prod_module( f, args.rep, dp_name, N )

   # write the nadder module
   with open( os.path.join( args.dest_dir, nadder_name + ".v" ), 'w' ) as f:
      write_nadder_module( f, nadder_name, N )

# Writes a stochatsic matrix multiply module to an output file, f.
# Parameters:
#  module_name, a string for the module
#  batch, an int specifying the batch size (in a matrix mult MxN * NxO, M is batch size)
#  inpt, an int specifying the input feature size (N)
#  outpt, an int specifying the output feature size (O)
def write_matrix_module( f, module_name, batch, inpt, outpt ):
   # compute the log base 2 of the input, 
   # this is how many select streams are required
   select_width = clogb2( inpt )

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
   write_line( f, "parameter BATCH_SIZE = " + str(batch) + "; // M", 1 )
   write_line( f, "parameter INPUT_FEATURES = " + str(inpt) + "; // N", 1 )
   write_line( f, "parameter OUTPUT_FEATURES = " + str(outpt) + "; // O", 1 )
   write_line( f, "parameter SELECT_WIDTH = " + str(select_width) + ";", 1 )
   write_line( f, "" )
   write_line( f, "// inputs and outputs", 1 )
   write_line( f, "input                                      clk;", 1 )
   write_line( f, "input                                      rst;", 1 )
   write_line( f, "input [BATCH_SIZE*INPUT_FEATURES-1:0]      inputStreams;", 1 )
   write_line( f, "input [OUTPUT_FEATURES*INPUT_FEATURES-1:0] weightStreams;", 1 )
   write_line( f, "input [SELECT_WIDTH-1:0]                 sel;", 1 )
   write_line( f, "output [BATCH_SIZE*OUTPUT_FEATURES-1:0]    outputStreams;", 1 )
   write_line( f, "output                                     outputWriteEn;", 1 )
   write_line( f, "" )
   write_line( f, "genvar i;", 1 )
   write_line( f, "genvar j;", 1 )
   write_line( f, "generate", 1 )
   write_line( f, "for( i = 0; i < BATCH_SIZE; i = i + 1) begin : dot_prod_loop", 2 )
   write_line( f, "for( j = 0; j < OUTPUT_FEATURES; j = j + 1) begin", 3 )
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

# Writes a stochastic dot_product module to the file, f.
# Parameters:
#  f, the file to write to
#  rep, a string for the stochastic represntation type (uni or bi)
#  module_name, a string for the module name
#  length, an int which specifies the length of the input vectors to the module
def write_dot_prod_module( f, rep, module_name, length ):
   # compute number of select streams
   select_width = clogb2( length )
   
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
   write_line( f, "parameter LENGTH = " + str(length) + ";", 1 )
   write_line( f, "parameter SELECT_WIDTH = " + str(select_width) + ";", 1 )
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

   if rep == 'uni':
      write_line( f, "sc_multiplier(.x(data[i]), .y(weights[i]), .res(mult_out[i]));", 3 )
   if rep == 'bi':
      write_line( f, "sc_multiplier_bi(.x(data[i]), .y(weights[i]), .z(mult_out[i]));", 3 )

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

# Writes a sc_nadder module. This module adds n inputs in the stochastic domain.
# Parameters:
#  f, the file to write to
#  module_name, a string for the module name
#  n, an integer which specifies the number of inputs to the adder module
def write_nadder_module( f, module_name, n ):
   # compute number of select streams needed 
   # select_width = int(math.log( n, 2 ))
   select_width = clogb2( n )

   # write the header comment
   write_header_nadder( f )
   
   write_line( f, "module " + module_name + "(" )
   write_line( f, "x,", 1 )
   write_line( f, "sel,", 1 )
   write_line( f, "out", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter INPUT_STREAMS = " + str(n) + ";", 1 )
   write_line( f, "parameter SELECT_WIDTH = " + str(select_width) + ";", 1 )
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
   write_line( f, "// The input 'sel' must be the concatenation of log2(INPUT_STREAMS) number of" )
   write_line( f, "// un-correlated stochastic streams (each with value=0.5)." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

   return


#-----------Testbench Generation------------#
# Function which opens and writes testbench files for the verilog modules
# generated (and specified by the users input arguments).
def generate_testbenches( args ):
   # if a module name is supplied, concatenate module names
   mm_tb_name = "sc_matrix_mult_tb"
   dp_tb_name = "sc_dot_product_tb"
   nadder_tb_name = "sc_nadder_tb"
   if args.module_name is not "":
      mm_tb_name += "_" + args.module_name
      dp_tb_name += "_" + args.module_name
      nadder_tb_name += "_" + args.module_name

   # make a folder for the testbenches called 'tb'
   tb = args.dest_dir + "/tb"
   if not os.path.exists( tb ):
      os.makedirs( tb )

   # write the matrix multiply testbench
   with open( os.path.join( tb, mm_tb_name + ".v" ), 'w' ) as f:
      #write_mm_tb( f, 
      pass

   # write the dot product testbench
   with open( os.path.join( tb, dp_tb_name + ".v" ), 'w' ) as f:
     #write_dp_tb( f, 
      pass

   # write the nadder testbench module
   with open( os.path.join( tb, nadder_tb_name + ".v" ), 'w' ) as f: 
      write_nadder_tb( f, nadder_tb_name, args.input_size )

# Writes a testbench module for the generated sc_nadder.
# Parameter:
#  f, the file to write to
#  module_name, the name of the testbench module
#  n, an int, the number of inputs to the nadder
def write_nadder_tb( f, module_name, n ):
   # write the header comment
   # write_nadder_tb_header( f )

   # compute number of select streams needed 
   select_width = clogb2( n )

   # compute the max possible number of input stream permutations
   # and select stream permutations
   input_count = int(math.pow( 2, n ))
   select_count = int(math.pow( 2, select_width ))

   write_line( f, "`timescale 1ns / 10ps" )  
   write_line( f, "" )
   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter INPUT_STREAMS = " + str(n) + ";", 1 )
   write_line( f, "parameter SELECT_WIDTH = " + str(select_width) + ";", 1 ) 
   write_line( f, "" )
   write_line( f, "reg [INPUT_STREAMS-1:0] x;", 1 )
   write_line( f, "reg [SELECT_WIDTH-1:0]  sel;", 1 )
   write_line( f, "wire                    out;", 1 )
   write_line( f, "" )
   write_line( f, "sc_nadder dut(.x(x), .sel(sel), .out(out));", 1 )
   write_line( f, "" )
   write_line( f, "integer errors;", 1 )
   write_line( f, "initial errors = 0;", 1 )
   write_line( f, "" )
   write_line( f, "integer i;", 1 )
   write_line( f, "integer s;", 1 )
   write_line( f, "initial begin", 1 )
   write_line( f, "// initialize inputs", 2 )
   write_line( f, "x = 0;", 2 )
   write_line( f, "sel = 0;", 2 )
   write_line( f, "#25;", 2 )
   write_line( f, "" )
   write_line( f, "// for all input stream permutations, test each possible select permutation", 2 )
   write_line( f, "for(i = 0; i < " + str(input_count) + "; i = i + 1) begin", 2 ) 
   write_line( f, "x = i;", 3 )
   write_line( f, "for(s = 0; s < " + str(select_count) + "; s = s + 1) begin", 3 )
   write_line( f, "sel = s;", 4 )
   write_line( f, "#5;", 4 )
   write_line( f, "if( x[s] != out ) begin", 4 )
   write_line( f, "$display( \"Error incorrect output. Input streams: %B, Select streams: %B, out: %d\", x, sel, out );", 5 )
   write_line( f, "errors = errors + 1;", 5 )
   write_line( f, "end", 4 )
   write_line( f, "#5;", 4 )
   write_line( f, "end", 3 )
   write_line( f, "end", 2 )
   write_line( f, "" )
   write_line( f, "// error summary", 2 )
   write_line( f, "if( errors > 0 ) begin", 2 )
   write_line( f, "$display(\"Validataion failure: %d error(s).\", errors);", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "$display(\"Validation successful.\");", 3 )
   write_line( f, "end", 2 )
   write_line( f, "" )
   write_line( f, "$stop;", 2 )
   write_line( f, "end", 1 )
   write_line( f, "endmodule // sc_nadder_tb" )

   return

#---------Helper functions-----------#
# Helper function to write to file, f.
# Writes string to file f with numTabs number of tabs before
# the string and a newline character after the string.
def write_line( f, string, numTabs=0 ):
   tab = ""
   for i in range(0,numTabs):
      tab += "   "
   f.write( tab + string + "\n" )

# Helper function to get the time and date in GMT
def get_time():
   return strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " GMT"

# Helper function. Computes the ceiling log base 2 of input.
def clogb2( x ):
   return int(math.ceil( math.log( x, 2 ) ))


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
   generate_modules( args )
   print( "done!" )
   print( "Generating Testbenches..." )
   generate_testbenches( args ) 
   print( "done!" )
