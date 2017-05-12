# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains functions to generata the core modules for
# stochastic matrix multiply. 

from common import *
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

   return

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
   write_line( f, "wire [BATCH_SIZE*OUTPUT_FEATURES-1:0] valids;", 1 )
   write_line( f, "generate", 1 )
   write_line( f, "for( i = 0; i < BATCH_SIZE; i = i + 1) begin : dot_prod_loop", 2 )
   write_line( f, "for( j = 0; j < OUTPUT_FEATURES; j = j + 1) begin", 3 )
   write_line( f, "sc_dot_product DOT_PRODUCT(.clk(clk),", 4 )
   write_line( f, "                .rst(rst),", 4 )
   write_line( f, "                .data(inputStreams[i*INPUT_FEATURES +: INPUT_FEATURES]),", 4 )
   write_line( f, "                .weights(weightStreams[j*INPUT_FEATURES +: INPUT_FEATURES]),", 4 )
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
   write_line( f, "result,", 1 )
   write_line( f, "valid", 1 )
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
   write_line( f, "output                   valid;", 1 )
   write_line( f, "" ) 
   write_line( f, "// multipication modules, for element wise multiplication of data and weights", 1 )
   write_line( f, "genvar i;", 1 )
   write_line( f, "wire [LENGTH-1:0] mult_out;", 1 )
   write_line( f, "generate", 1 )
   write_line( f, "for( i = 0; i < LENGTH; i = i + 1) begin : mult", 2 )

   if rep == 'uni':
      write_line( f, "sc_multiplier MULT(.x(data[i]), .y(weights[i]), .res(mult_out[i]));", 3 )
   if rep == 'bi':
      write_line( f, "sc_multiplier_bi MULT(.x(data[i]), .y(weights[i]), .z(mult_out[i]));", 3 )

   write_line( f, "end", 2 )
   write_line( f, "endgenerate", 1 )
   write_line( f, "" )
   write_line( f, "// direct multiplication output to an intermediate register", 1 )
   write_line( f, "reg [LENGTH-1:0] product_streams;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst == 1'b1 ) begin", 2 )
   write_line( f, "product_streams <= 0;", 3 )
   write_line( f, "end else begin", 2 ) 
   write_line( f, "product_streams <= mult_out;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "// shift the slect streams by 1, this is to wait for the multiplication to complete", 1 )
   write_line( f, "reg [SELECT_WIDTH-1:0] select;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst == 1'b1 ) begin", 2 )
   write_line( f, "select <= 0;", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "select <= sel;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "// add all element-wise products", 1 )
   write_line( f, "wire adder_res;", 1 )
   write_line( f, "sc_nadder NADDER(.x(product_streams), .sel(select), .out(adder_res));", 1 )
   write_line( f, "" )
   write_line( f, "// direct adder output to register and then to final output", 1 )
   write_line( f, "reg i_result;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst == 1'b1 ) begin", 2 )
   write_line( f, "i_result <= 0;", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "i_result <= adder_res;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "assign result = i_result;", 1 )
   write_line( f, "" )
   write_line( f, "// Use shift register to indicate when module output is valid", 1 )
   # Ill have to change the shift register type (after I implement the alaghi adder stuff)
   # TODO
   write_line( f, "shift_2_register SHIFT2(.clk(clk), .rst(rst), .data_in(1'b1), .data_out(valid));", 1 )
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

