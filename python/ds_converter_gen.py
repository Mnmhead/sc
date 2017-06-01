# Copyright (c) Gyorgy Wyatt Muntean 2017
# Python script to generate a Verilog sd_converter module.
# A ds_converter converts binary numbers to stochastic bitstreams
# by comparing a noise source stream (rng) to the binary number and genrating
# a series of 1's and 0's absed on the comparison.
# The precision of the binary input (and rng input) must be specified.

from common import *
import os

# Function to open and write a ds_converter module
#  dest, the directory to write the file into
#  precision, the bitwidth of the binary input and rng input
def generate( dest, precision ):
   with open( os.path.join( dest, DS_CONVERTER + ".v" ), 'w' ) as f:
      write_header_ds_converter( f ) 
      write_ds_converter_module( f, DS_CONVERTER, precision )

# Write a digital to stochastic converter module.
# Parameters:
#  f, the file to write to
#  module_name, a string, the name of the module
#  precision, an integer, the precision of the input binary number and
#     input random number
def write_ds_converter_module( f, module_name, precision ):
   write_line( f, "module " + module_name + "(" )
   write_line( f, "in,", 1 )
   write_line( f, "rng,", 1 )
   write_line( f, "out", 1 )
   write_line( f, ");" )
   write_line( f, "parameter PRECISION = " + str(precision) + ";", 1 )
   write_line( f, "" )
   write_line( f, "input [PRECISION-1:0] in;", 1 )
   write_line( f, "input [PRECISION-1:0] rng;", 1 )
   write_line( f, "output out;", 1 )
   write_line( f, "" )
   write_line( f, "assign out = (rng < in) ? 1 : 0;", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

def write_header_ds_converter( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The module represents a digital to stochastic converter." )
   write_line( f, "//" )
   write_line( f, "// Note: Conversion is from digital to stochastic uni-polar representation." )
   write_line( f, "// The range of each stochastic bitstream produced is [0,1]." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

