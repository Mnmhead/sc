# Copyright (c) Gyorgy Wyatt Muntean 2017
# Python script to generate a Verilog SNG module.
# A SNG module takes binary numbers as input and outputs a
# stochastic bitstream representing the binary number in the
# stochastic domain.

from common import *
import ds_converter_gen as ds_gen
import os

# Function to open and write a SNG module to a file.
# The SNG depends on a ds_converter, so a ds_converter is written as well.
#  dest, the directory to write the file into
#  precision, the bitwidth of the binary input
def generate( dest, precision ):
   ds_gen.generate( dest, precision )
   
   with open( os.path.join( dest, SNG + ".v" ), 'w' ) as f:
      write_header_sng( f ) 
      write_sng_module( f, SNG, precision )
     
# Writes a stochastic number generator module.
# Parameters:
#  f, the file to write to
#  module_name, a string, the name of the module
#  precision, an integer, the precision of the input binary number and
#     input random number
#  rng, a string, specifies the kind of noise source for the stochastic
#     number generator. Options are: LFSR, COUNTER, REVERSECOUNTER (VANDERCORPIT?)
def write_sng_module( f, module_name, precision ):
   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter PRECISION = " + str(precision) + ";", 1 ) 
   write_line( f, "" )
   write_line( f, "input clk;", 1 ) 
   write_line( f, "input rst;", 1 ) 
   write_line( f, "input [PRECISION-1] in;", 1 ) 
   write_line( f, "input [PRECISION-1] rng;", 1 ) 
   write_line( f, "output out;", 1 ) 
   write_line( f, "" )
   write_line( f, "// pass the noise and input to the converter and clock the output", 1 ) 
   write_line( f, "reg ds_out [1:0];", 1 ) 
   write_line( f, "ds_converter DS_CONVERT(.in(in), .rng(rng), .out(ds_out[0]));", 1 ) 
   write_line( f, "" )
   write_line( f, "always @(posedge clk) begin", 1 ) 
   write_line( f, "if (rst == 1) begin", 2 ) 
   write_line( f, "ds_out[0] = 0;", 3 ) 
   write_line( f, "ds_out[1] = 0;", 3 ) 
   write_line( f, "end else begin", 2 ) 
   write_line( f, "ds_out[1] <= ds_out[0];", 3 ) 
   write_line( f, "end", 2 ) 
   write_line( f, "end", 1 ) 
   write_line( f, ""  )
   write_line( f, "assign out = ds_out[1];", 1 ) 
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

def write_header_sng( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The module represents a stochastic number generator." )
   write_line( f, "// Requires an input noise source (either lfsr, counter, reversed counter," )
   write_line( f, "// vander corpi, etc)" )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )
