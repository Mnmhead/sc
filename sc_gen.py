# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains functions to generate the core modules for
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
   alaghi_nadder_name = ALAGHI_NADDER

   # Write the supporting IP, the dot_product and nadder.
   if ( args.alaghi ):
      with open( os.path.join( args.dest_dir, alaghi_nadder_name + ".v" ), 'w' ) as f:
         write_alaghi_nadder_module( f, alaghi_nadder_name, N ) 
   else:
      with open( os.path.join( args.dest_dir, nadder_name + ".v" ), 'w' ) as f:
         write_nadder_module( f, nadder_name, N )

   with open( os.path.join( args.dest_dir, dp_name + ".v" ), 'w' ) as f:
      write_dot_prod_module( f, dp_name, N, args.rep, args.alaghi )

   # write the matrix multiply module
   with open( os.path.join( args.dest_dir, mat_mult_name + ".v" ), 'w' ) as f: 
      write_matrix_module( f, mat_mult_name, M, N, O )

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

# Writes a stochastic dot_product module to the file, f.
# Parameters:
#  f, the file to write to
#  rep, a string for the stochastic represntation type (uni or bi)
#  module_name, a string for the module name
#  length, an int which specifies the length of the input vectors to the module
def write_dot_prod_module( f, module_name, length, rep = "uni", alaghi = False ):
   # compute number of select streams
   select_width = clogb2( length )
   
   # write the header comment
   write_header_dot_prod( f )

   write_line( f, "module " + module_name + "(" )
   write_line( f, "clk,", 1 )
   write_line( f, "rst,", 1 )
   write_line( f, "data,", 1 )
   write_line( f, "weights,", 1 )
   if not alaghi:
      write_line( f, "sel,", 1 )
   write_line( f, "result,", 1 )
   write_line( f, "valid", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter LENGTH = " + str(length) + ";", 1 )
   if not alaghi:
      write_line( f, "parameter SELECT_WIDTH = " + str(select_width) + ";", 1 )
   write_line( f, "" )
   write_line( f, "// inputs and outputs", 1 )
   write_line( f, "input                    clk;", 1 )
   write_line( f, "input                    rst;", 1 )
   write_line( f, "input [LENGTH-1:0]       data;", 1 )
   write_line( f, "input [LENGTH-1:0]       weights;", 1 )
   if not alaghi:
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
   if not alaghi:
      write_line( f, "// shift the slect streams by 1 cycle, must wait for multiplication to complete", 1 )
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
   if alaghi:
      write_line( f, "alaghi_nadder NADDER(.clk(clk), .rst(rst), .inpts(product_streams), .out(adder_res));", 1 )
   else:
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

   delay = None
   if alaghi:
      # delay for alaghi tree is one cycle for every level, plus one for
      # final output register.
      delay = int(clogb2( length )) + 1
   else:
      # two clock cycle delay for standard dot product
      # 1 cycle for multiplication, 1 for addition (single mux)
      delay = 2

   write_line( f, "shift_" + str(delay) + "_register SHIFT" + str(delay) \
                  + "(.clk(clk), .rst(rst), .data_in(1'b1), .data_out(valid));", 1 )
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

# Writes an alaghi n-input adder module. 
# Parameters:
# f, the file to write to
# module_name, a string for the module name
# n, an integer, specifies the number of inputs
def write_alaghi_nadder_module( f, module_name, n ):
   # write the module header
   write_header_alaghi_nadder( f )

   write_line( f, "module " + module_name + "(" )
   write_line( f, "clk,", 1 )
   write_line( f, "rst,", 1 )
   write_line( f, "inpts,", 1 )
   write_line( f, "out", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "input clk;", 1 )
   write_line( f, "input rst;", 1 )
   write_line( f, "input [" + str(n-1) + ":0] inpts;", 1 )
   write_line( f, "output out;", 1 )
   write_line( f, "" )

   # Arrays are for storing the wires, registers, and alaghi adder module
   # information needed. The contents of the arrays are used to write the verilog
   # module after determining the structure of the adder tree.
   wire_strs = []
   sum_reg_strs = []
   alaghi_modules = []

   # initialize the first layer of input names
   input_names = []
   for i in range(n):
      input_names.append( "inpts[" + str(i) + "]" )

   # call the helper routine and generate each layer of alaghi adders
   layer_num = 1
   while( n >= 2 ):
      wires = []
      sum_regs = []
      alaghi_tuples = []
      compute_layer( n, layer_num, input_names, wires, sum_regs, alaghi_tuples )

      # append generated wires, registers, adders to the global list
      wire_strs.extend( wires )
      sum_reg_strs.extend( sum_regs )
      alaghi_modules.extend( alaghi_tuples )

      # update next layer inputs
      input_names = sum_regs
      n = len(sum_regs)
      layer_num += 1

	# Write all the wires, registers and adders to the file
   write_line( f, "// Wires for this tree. The first number specifies the level of the tree.", 1 )
   write_line( f, "// The second number is the 'name' (or index) of the wire within the level it resides.", 1 )

   # write all wire declarations
   for i in range(len(wire_strs)):
      write_line( f, "wire " + wire_strs[i] + ";", 1 )

   write_line( f, "" )
   write_line( f, "// Registers for each level of output.", 1 )

   # write all register declarations
   for i in range(len(sum_reg_strs)):
      write_line( f, "reg " + sum_reg_strs[i] + ";", 1 )

   write_line( f, "" )
   write_line( f, "// Write register assignments", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )

   # write wire->register assignments
   for i in range(len(wire_strs)):
      write_line( f, sum_reg_strs[i] + " <= " + wire_strs[i] + ";", 2 )

   write_line( f, "end", 1 )
   write_line( f, "" )

   # write adder modules
   for i in range(len(alaghi_modules)):
      (in1, in2, out) = alaghi_modules[i]
      write_line( f, "alaghi_adder ADDER" + str(i) + "(.clk(clk), .rst(rst), " \
                     + ".x(" + in1 + "), .y(" + in2 + "), " \
                     + ".out(" + out + "));", 1 )

   last_out = len(sum_reg_strs) - 1
   write_line( f, "" )
   write_line( f, "assign out = " + sum_reg_strs[last_out] + ";", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

# Helper function to compute the wire, registers, and adders for a layer of
# the adder tree.
#
# n, an int for the number of inputs to this layer
# layer_num, an int specifying the layer number (used for naming)
# input_names, the verilog names of the inputs to this layer
#
# Returns a list of wires, registers, and adder modules through 
# the return parameters: wires, sum_regs, and alaghi_tuples.
def compute_layer( n, layer_num, input_names, wires, sum_regs, alaghi_tuples):
   wire_count = 0

   while( n > 1 ):
      # t, the largest power of 2 within n
      t = math.pow( 2, flogb2( n ) )

      # pair up inputs, generate an adder, and generate a wire and a reg for ouput
      i = 0
      while( i < t ):
         wire_str = "sum_" + str(layer_num) + "_" + str(wire_count)
         wires.append(wire_str)
         reg_str = "sumreg_" + str(layer_num) + "_" + str(wire_count)
         sum_regs.append(reg_str)
         alaghi_tup = (input_names[i], input_names[i+1], wire_str)
         alaghi_tuples.append( alaghi_tup )

         wire_count += 1
         i = i + 2

      n = n - t

   # if there is a left-over input, pair it up with a constant 0 input
   # this maintains the scaling factor
   if( n == 1 ):
      last_index = len(input_names) - 1

      wire_str = "sum_" + str(layer_num) + "_0const"
      wires.append(wire_str)
      reg_str = "sumreg_" + str(layer_num) + "_0const"
      sum_regs.append(reg_str)
      alaghi_tup = (input_names[last_index], str(0), wire_str)
      alaghi_tuples.append( alaghi_tup )

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

# Writes the header comment for the sc_dot_product module.
# The file written to is the parameter, f.
def write_header_dot_prod( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a dot product of two vectors in the" )
   write_line( f, "// stochastic domain." )
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

# Writes the header comment for the alaghi_nadder module.
# The file written to is the parameter, f.
def write_header_alaghi_nadder( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a tree of alaghi adders." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

