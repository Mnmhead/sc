# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains functions to generate the core modules for
# stochastic matrix multiply. 

from common import *
from shiftreg_gen import *
import os

# Generates modules in the stochastic domain. 
# Opens and writes to files.
# The contents of the files are specified by the users input.
def generate( args ):
   M = args.batch_size
   N = args.input_size
   O = args.output_size

   # if a module name is supplied, concatenate module names
   mat_mult_name = MATRIX
   dp_name = DOT_PROD
   nadder_name = NADDER
   alaghi_nadder_name = ALAGHI_NADDER

   # Write the supporting IP, the dot_product, shift_register, and nadder.
   if ( args.alaghi ):
      with open( os.path.join( args.dest_dir, alaghi_nadder_name + ".v" ), 'w' ) as f:
         write_alaghi_nadder_module( f, alaghi_nadder_name, N ) 
     	
      shift = int(clogb2(args.input_size)) + 2
      shift_name = "shift_" + str(shift) + "_register"
      with open( os.path.join( args.dest_dir, shift_name + ".v" ), 'w' ) as f:
         write_shiftreg_module( f, shift_name, shift )

   else:
      with open( os.path.join( args.dest_dir, nadder_name + ".v" ), 'w' ) as f:
         write_nadder_module( f, nadder_name, N )

      shift = 2
      shift_name = "shift_" + str(shift) + "_register"
      with open( os.path.join( args.dest_dir, shift_name + ".v" ), 'w' ) as f:
         write_shiftreg_module( f, shift_name, shift )

   with open( os.path.join( args.dest_dir, dp_name + ".v" ), 'w' ) as f:
      write_dot_prod_module( f, dp_name, N, args.rep, alaghi=args.alaghi )

   # write the matrix multiply module
   with open( os.path.join( args.dest_dir, mat_mult_name + ".v" ), 'w' ) as f: 
      write_matrix_module( f, mat_mult_name, M, N, O, alaghi=args.alaghi)

# Writes a stochatsic matrix multiply module to an output file, f.
# Parameters:
#  module_name, a string for the module
#  batch, an int specifying the batch size (in a matrix mult MxN * NxO, M is batch size)
#  inpt, an int specifying the input feature size (N)
#  outpt, an int specifying the output feature size (O)
def write_matrix_module( f, module_name, batch, inpt, outpt, alaghi = False ):
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
   if not alaghi:
      write_line( f, "sel,", 1 )
   write_line( f, "outputStreams,", 1 )
   write_line( f, "outputWriteEn", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter BATCH_SIZE = " + str(batch) + "; // M", 1 )
   write_line( f, "parameter INPUT_FEATURES = " + str(inpt) + "; // N", 1 )
   write_line( f, "parameter OUTPUT_FEATURES = " + str(outpt) + "; // O", 1 )
   if not alaghi:
      write_line( f, "parameter SELECT_WIDTH = " + str(select_width) + ";", 1 )
   write_line( f, "" )
   write_line( f, "// inputs and outputs", 1 )
   write_line( f, "input                                      clk;", 1 )
   write_line( f, "input                                      rst;", 1 )
   write_line( f, "input [BATCH_SIZE*INPUT_FEATURES-1:0]      inputStreams;", 1 )
   write_line( f, "input [OUTPUT_FEATURES*INPUT_FEATURES-1:0] weightStreams;", 1 )
   if not alaghi:
      write_line( f, "input [SELECT_WIDTH-1:0]                 sel;", 1 )
   write_line( f, "output [BATCH_SIZE*OUTPUT_FEATURES-1:0]    outputStreams;", 1 )
   write_line( f, "output                                     outputWriteEn;", 1 )
   write_line( f, "" )
   write_line( f, "genvar i;", 1 )
   write_line( f, "genvar j;", 1 )
   write_line( f, "wire [BATCH_SIZE*OUTPUT_FEATURES-1:0] valids;", 1 )
   write_line( f, "generate", 1 )
   write_line( f, "for( i = 0; i < BATCH_SIZE; i = i + 1) begin : dot_prod_loop", 2 )
   write_line( f, "for( j = 0; j < OUTPUT_FEATURES; j = j + 1) begin", 3 )
   write_line( f, "sc_dot_product DOT_PRODUCT(.clk(clk),", 4 )
   write_line( f, "                .rst(rst),", 4 )
   write_line( f, "                .data(inputStreams[i*INPUT_FEATURES +: INPUT_FEATURES]),", 4 )
   write_line( f, "                .weights(weightStreams[j*INPUT_FEATURES +: INPUT_FEATURES]),", 4 )
   if not alaghi:
      write_line( f, "                .sel(sel),", 4 )
   write_line( f, "                .result(outputStreams[(i*OUTPUT_FEATURES)+j]),", 4 )
   write_line( f, "                .valid(valids[(i*OUTPUT_FEATURES)+j]));", 4 )
   write_line( f, "end", 3 )
   write_line( f, "end", 2 )
   write_line( f, "endgenerate", 1 )
   write_line( f, "" )
   write_line( f, "// later we will incorporate this signal", 1 )
   write_line( f, "assign outputWriteEn = (valids[0] == 1'b1);", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

# Writes a sc_nadder module.
# Parameters:
#  f, the file to write to
#  module_name, a string for the module name
#  n, an integer which specifies the number of inputs to the adder module
def write_nadder_module( f, module_name, n ):
   # compute number of select streams needed 
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
   write_line( f, "endmodule // " + module_name )

# Writes the header comment for the sc_matrix_mult module.
# This comment nincludes a timestamp of when the file was genertaed, in GMT.
def write_header_mat_mult( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: This module represents matrix multiply in the stochastic domain." )
   write_line( f, "// The inputs to this module are two flattened matrices A and B," )
   write_line( f, "// where A has dimensions MxN and B has dimensions NxO." )
   write_line( f, "// The input matrix B is actually the transpose of B (still flattened)" )
   write_line( f, "// This results in a matrix C with dimensions MxO." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

# Writes the header comment for the sc_nadder module.
# The file written to is the parameter, f.
def write_header_nadder( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a multi-input adder in the stochastic" )
   write_line( f, "// domain." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )
