# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains a function to generate a Verilog module
# representing a alaghi adder tree. 

from common import *
import os

# Opens and writes a alaghi adder tree module to a file.
#  dest, a string, the directory to write the file
#  n, an int, the number of inputs to the adder tree (hence nadder)
def generate( dest, n ):
   with open( os.path.join( dest, ALAGHI_NADDER + ".v" ), 'w' ) as f:
      write_header_alaghi_nadder( f )
      write_alaghi_nadder_module( f, ALAGHI_NADDER, n )

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

# Writes the header comment for the alaghi_nadder module.
# The file written to is the parameter, f.
def write_header_alaghi_nadder( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a tree of alaghi adders." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

