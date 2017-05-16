# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains functions to generata the core modules for
# stochastic matrix multiply. 

from common import *
import os

def generate_alaghi_nadder( n, module_name="alaghi_nadder" ):
   
   with open( os.path.join( ".", module_name + ".v" ), 'w' ) as f:
      write_alaghi_nadder_module( f, n, module_name )

   return

def write_alaghi_nadder_module( f, n, module_name="alaghi_nadder" ):
   write_line( f, "module " + module_name + "();" )
   write_line( f, "" )
   write_line( f, "input clk;", 1 )
   write_line( f, "input rst;", 1 )
   write_line( f, "input [" + str(n-1) + ":0] inpts;", 1 )
   write_line( f, "output out;", 1 )
   write_line( f, "" )
   
   # now we need to build up the strings we want to print
   # to the file. 
   # 1. we will want to print the output wires and output registers 
   wire_strs = []
   sum_reg_strs = []
   # 2. we will want to print clocking, eesentially reg[i] <= wire[i]
   # 3. we will want to print assignment
   #     this involves printing the alaghi adder module with inputs and output
   #     (we can store the inputs and output as a tuple)
   #     (x, y, out)
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
      num_regs = generate_layer( n, layer_num, input_names, wires, sum_regs, alaghi_tuples )

      # update next layer inputs
      input_names = wires
      n = len(wires)
      layer_num += 1

      # append generated wires, registers, adders to the global list
      wire_strs.extend( wires )
      sum_reg_strs.extend( sum_regs )
      alaghi_modules.extend( alaghi_tuples )

   
   # now we writ all the wires, registers and adders to the file
   print( wire_strs )
   print( "" )
   print( "" )
   print( sum_reg_strs )
   print( "" )
   print( "" )
   print( alaghi_modules )

   write_line( f, "// wires for this tree. The first number specifies the level of the tree.", 1 )
   write_line( f, "// The second number is the 'name' (or index) of the wire within its level.", 1 )
   for i in range(len(wire_strs)):
      write_line( f, "wire " + wire_strs[i] + ";", 1 )

   write_line( f, "" )
   write_line( f, "// registers for each level of output.", 1 )
   for i in range(len(sum_reg_strs)):
      write_line( f, "reg " + sum_reg_strs[i] + ";", 1 )

   write_line( f, "" )
   write_line( f, "always @(posedge clk) begin", 1 )
   for i in range(len(wire_strs)):
      write_line( f, sum_reg_strs[i] + " <= " + wire_strs[i] + ";", 2 )

   write_line( f, "end", 1 )
   write_line( f, "" )
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


def generate_layer( n, layer_num, input_names, wires, sum_regs, alaghi_tuples):
   # counter for number of outputs of this layer
   num_out = 0

   while( n > 1 ):
      # grab the largest power of 2 within n
      t = math.pow( 2, flogb2( n ) )

      # pair up inputs, generate an adder, and generate a wire and a reg for ouput
      i = 0
      while( i < t ):
         wire_str = "sum_" + str(layer_num) + "_" + str(i/2)
         wires.append(wire_str)
         reg_str = "sumreg_" + str(layer_num) + "_" + str(i/2)
         sum_regs.append(reg_str)
         alaghi_tup = (input_names[i], input_names[i+1], wire_str)
         alaghi_tuples.append( alaghi_tup )

         i = i + 2
         num_out += 1

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

      num_out += 1
  
   return num_out

generate_alaghi_nadder( 4 )
