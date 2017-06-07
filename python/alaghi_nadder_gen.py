# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains a function to generate a Verilog module
# representing a alaghi adder tree. 

from common import *
import numpy as np
import os
from pysc.core.arithmetic import *
from pysc.rngs.lfsr import *

# alaghi adder testbench constants
_ALAGHI_INPUT_FN = "adder_inputs.mif"
_ALAGHI_RES_FN = "adder_results.mif"
_ALAGHI_TEST_SIZE = 100


# Opens and writes a alaghi adder tree module to a file.
#  dest, a string, the directory to write the file
#  n, an int, the number of inputs to the adder tree (hence nadder)
def generate( dest, n, test = True ):
   with open( os.path.join( dest, ALAGHI_NADDER + ".v" ), 'w' ) as f:
      write_header_alaghi_nadder( f )
      write_alaghi_nadder_module( f, ALAGHI_NADDER, n )

   if test:
      (tb, data) = makeTestDir( dest )
      tb_name = ALAGHI_NADDER + "_tb"

      # write the alaghi adder testbench module
      gen_alaghi_data( data, n, _ALAGHI_TEST_SIZE )
      with open( os.path.join( tb, tb_name + ".v" ), 'w' ) as f:
         # write the header comment
         write_alaghi_nadder_tb_header( f )
         write_alaghi_nadder_tb( f, tb_name, n )

# Writes an alaghi n-input adder module.
# Parameters:
#  f, the file to write to
#  module_name, a string for the module name
#  n, an integer, specifies the number of inputs
def write_alaghi_nadder_module( f, module_name, n ):
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
   next_input = 0

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
         alaghi_tup = (input_names[next_input], input_names[next_input+1], wire_str)
         alaghi_tuples.append( alaghi_tup )

         wire_count += 1
         next_input = next_input + 2
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

# Writes the test bench for the alaghi n-adder module.
# 	f, the file to write to
#  module_name, the name of the testbench
#	n, the number of inputs to the nadder dut
def write_alaghi_nadder_tb( f, module_name, n ):
   delay = int(clogb2( n )) - 1 

   write_line( f, "`timescale 1ns / 10ps" )
   write_line( f, "" )
   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter INPUT_STREAMS = " + str(n) + ";", 1 ) 
   write_line( f, "parameter DELAY =         " + str(delay) + ";", 1 ) 
   write_line( f, "parameter INPUTS =        \"" + _ALAGHI_INPUT_FN + "\";", 1 ) 
   write_line( f, "parameter ADDER_RESULT =  \"" + _ALAGHI_RES_FN + "\";", 1 ) 
   write_line( f, "parameter TEST_LENGTH =   " + str(_ALAGHI_TEST_SIZE) + ";", 1 ) 
   write_line( f, "" )
   write_line( f, "// modules inputs and outputs", 1 ) 
   write_line( f, "reg                      clk;", 1 ) 
   write_line( f, "reg                      rst;", 1 ) 
   write_line( f, "wire [INPUT_STREAMS-1:0] inpts;", 1 ) 
   write_line( f, "wire                     out;", 1 ) 
   write_line( f, "" )
   write_line( f, "// read input data and expected results data", 1 ) 
   write_line( f, "reg [INPUT_STREAMS-1:0] test_inputs [TEST_LENGTH-1:0];", 1 ) 
   write_line( f, "reg expected_results [TEST_LENGTH-1:0];", 1 ) 
   write_line( f, "initial begin", 1 ) 
   write_line( f, "$readmemb(INPUTS, test_inputs, 0, TEST_LENGTH-1);", 2 ) 
   write_line( f, "$readmemb(ADDER_RESULT, expected_results, 0, TEST_LENGTH-1);", 2 ) 
   write_line( f, "end", 1 ) 
   write_line( f, "" )
   write_line( f, "// Test input data assignment logic", 1 ) 
   write_line( f, "reg [TEST_LENGTH-1:0] test_index;", 1 ) 
   write_line( f, "initial test_index = 0;", 1 ) 
   write_line( f, "always @(posedge clk) begin", 1 ) 
   write_line( f, "if( rst == 1'b1 ) begin", 2 ) 
   write_line( f, "test_index <= 0;", 3 ) 
   write_line( f, "end else begin", 2 ) 
   write_line( f, "test_index <= test_index + 1;", 3 ) 
   write_line( f, "end", 2 ) 
   write_line( f, "end", 1 ) 
   write_line( f, "assign inpts = test_inputs[test_index];", 1 ) 
   write_line( f, "" )
   write_line( f, "" )
   write_line( f, "// Output checking and error handling", 1 ) 
   write_line( f, "reg valid;", 1 ) 
   write_line( f, "reg [TEST_LENGTH-1:0] valid_delay;", 1 ) 
   write_line( f, "initial valid_delay = 0;", 1 ) 
   write_line( f, "always @(posedge clk) begin", 1 ) 
   write_line( f, "if( rst ) begin", 2 ) 
   write_line( f, "valid <= 0;", 3 ) 
   write_line( f, "valid_delay <= 0;", 3 ) 
   write_line( f, "end else begin", 2 ) 
   write_line( f, "if( valid_delay == DELAY ) begin", 3 )
   write_line( f, "valid <= 1;", 4 )
   write_line( f, "end else begin", 3 )
   write_line( f, "valid_delay <= valid_delay + 1;", 4 )
   write_line( f, "end", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "integer result_index;", 1 )
   write_line( f, "integer errors;", 1 )
   write_line( f, "initial result_index = 0;", 1 )
   write_line( f, "initial errors = 0;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst ) begin", 2 )
   write_line( f, "result_index <= 0;", 3 )
   write_line( f, "end else if( valid == 1'b1 ) begin", 2 )
   write_line( f, "if( out != expected_results[result_index] ) begin", 3 )
   write_line( f, "$display(\"Error. Expected result %d does not match actual %d. On result index: %d\",", 4 )
   write_line( f, "expected_results[result_index], out, result_index);", 5 )
   write_line( f, "errors = errors + 1;", 4 )
   write_line( f, "end", 3 )
   write_line( f, "" )
   write_line( f, "result_index = result_index + 1;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "// Clock Generation", 1 )
   write_line( f, "parameter CLOCK_PERIOD=10;", 1 )
   write_line( f, "initial clk=1;", 1 )
   write_line( f, "always begin", 1 )
   write_line( f, "#(CLOCK_PERIOD/2);", 2 )
   write_line( f, "clk = ~clk;", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "// instantiate module", 1 )
   write_line( f, "alaghi_nadder dut(.clk(clk), .rst(rst), .inpts(inpts), .out(out));", 1 )
   write_line( f, "" )
   write_line( f, "initial begin", 1 )
   write_line( f, "// initialize inputs", 2 )
   write_line( f, "rst = 1;", 2 )
   write_line( f, "#(1*CLOCK_PERIOD);", 2 )
   write_line( f, "" )
   write_line( f, "// start sim", 2 )
   write_line( f, "rst = 0;", 2 )
   write_line( f, "#(TEST_LENGTH*CLOCK_PERIOD + 2*DELAY);", 2 )
   write_line( f, "" )
   write_line( f, "// error summary", 2 )
   write_line( f, "$display(\"Simulation complete.\");", 2 )
   write_line( f, "if( errors > 0 ) begin", 2 )
   write_line( f, "$display(\"Validataion failure: %d error(s).\", errors);", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "$display(\"Validation successful.\");", 3 )
   write_line( f, "end", 2 )
   write_line( f, "" )
   write_line( f, "$stop;", 2 )
   write_line( f, "end", 1 )
   write_line( f, "endmodule // " + module_name )

# Function to generate random input data for the alaghi adder.
# Parameters:
#  data_dir, the directory to write the files into
#  n, an int, the number of inputs to the adder
#  length, an int, the length of the stochastic streams
def gen_alaghi_data( data_dir, n, length ):
   # generate a random vector of size n
   inpt = np.random.randint( length, size = n )
   rng = lfsr_sequence( length, normalize = False )
   inputs = np.empty( (n, length), dtype = bool )
   for d in range(n):
      inputs[d, :] = rng < inpt[d]

   # Write the input data to a file
   with open( os.path.join( data_dir, _ALAGHI_INPUT_FN ), 'w' ) as f:
      for stream in range(length):
         s_str = stream_to_str( inputs[:,stream] )
         f.write( s_str + "\n" )

   # compute the result and write them to a file
   result = alaghi_adder( inputs )

   with open( os.path.join( data_dir, _ALAGHI_RES_FN ), 'w' ) as f:
      for res in result:
         if res:
            res_str = "1"
         else:
            res_str = "0"
         f.write( res_str + "\n" )

# This function could be facoted out to the arithmetic directory in pysc.
# Also pysc's sc_dot_product could call this function?
def alaghi_adder( inputs ):
   (dimensions, length) = inputs.shape
   dims = int(2 ** clogb2(dimensions))
   zero = np.zeros( length, dtype=bool )
   while dims > 1:
      x = 0
      while x in range(dims):
         op_a = zero if x >= dimensions else inputs[x, :]
         op_b = zero if x+1 >= dimensions else inputs[x+1, :]
         add_res = sc_add( op_a, op_b, select_mode = "ALAGHI" )
         if x == 0:
            inputs[0, :] = add_res
         else:
            inputs[x/2, :] = add_res
         x = x + 2

      dims = dims / 2

   return inputs[0, :]

# Writes the header comment for the alaghi_nadder module.
# The file written to is the parameter, f.
def write_header_alaghi_nadder( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a tree of alaghi adders." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

# Writes the header comment for alaghi_nadder testbench to file, f.
def write_alaghi_nadder_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: This module serves as a testbench for the alaghi_nadder module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )

# Helper function
# Takes in an array of 1's and 0's and outputs a string of
# those 1's and 0's concatenated.
# Characters of the stream are concatenated to the front,
# this is because we write the stream to the data file
# in a way that makes it easy for verilog's readmemb()
# to read the data.
def stream_to_str( stream, reverse = False ):
   s_str = ""
   for bit in stream:
      #s_str = "1" + s_str if bit else "0" + s_str
      if bit:
         s_str = "1" + s_str
      else:
         s_str = "0" + s_str

   return s_str

