# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains a function to generate a Verilog module 
# for stochastic dot product.

import alaghi_nadder_gen
from common import *
import os
import sc_nadder_gen
import shiftreg_gen

# Opens and writes a stochastic dot product module to a file.
#  dest, a string, the directory to write the file into
#  dimensions, an int, the dimension of the vectors to dot-product 
#  rep, the stochastic representation
#  alaghi, a boolean, specifies if alaghi adder tree is used
def generate( dest, dimensions, rep = "uni", alaghi = False ):
   # generate the shift_register
   delay = None
   if alaghi:
      # delay for alaghi tree is one cycle for every level, plus one for
      # final output register of the alaghi adder and another for the final
      # register of the dot product.
      delay = int(clogb2( dimensions )) + 2
      alaghi_nadder_gen.generate( dest, dimensions ) 
   else:
      # two clock cycle delay for standard dot product
      # 1 cycle for multiplication, 1 for addition (single mux)
      delay = 2
      sc_nadder_gen( dest, dimensions )      

   shiftreg_gen.generate( dest, delay )

   with open( os.path.join( dest, DOT_PROD + ".v" ), 'w' ) as f:
      write_header_dot_prod( f )
      write_dot_prod_module( f, DOT_PROD, dimensions, rep, alaghi )

# Writes a stochastic dot_product module to the file, f.
# Parameters:
#  f, the file to write to
#  rep, a string for the stochastic represntation type (uni or bi)
#  module_name, a string for the module name
#  dimensions, an int which specifies the length of the input vectors to the module
def write_dot_prod_module( f, module_name, dimensions, rep = "uni", alaghi = False ):
   # compute number of select streams
   select_width = clogb2( dimensions )

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
   write_line( f, "parameter LENGTH = " + str(dimensions) + ";", 1 )
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
   if alaghi:
      delay = int(clogb2( dimensions )) + 2
   else:
      delay = 2
   write_line( f, "shift_" + str(delay) + "_register SHIFT" + str(delay) \
                  + "(.clk(clk), .rst(rst), .data_in(1'b1), .data_out(valid));", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

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
