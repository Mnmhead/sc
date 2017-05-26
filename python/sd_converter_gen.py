# Copyright (c) Gyorgy Wyatt Muntean 2017
# Python script to generate a Verilog sd_converter module.
# A sd_converter converts bitstreams in the stochastic domain
# into the binary/digital domain.
# The precision of the binary output must be specified.

from common import *
import os

# Function to open and write a sd_converter module to a file.
#  dest, the directory to write the file into
#  precision, the bitwidth of the binary output
def generate( dest, precision ):
   with open( os.path.join( dest, SD_CONVERTER + ".v" ), 'w' ) as f:
      write_header_sd_converter( f ) 
      write_sd_converter_module( f, SD_CONVERTER, precision )

# Writes a digital to stochastic converter module.
# Parameters:
#  f, the file to write to
#  module_name, a string, the name of the module
#  precision, an integer, the precision of the output binary number
def write_sd_converter_module( f, module_name, precision ):
   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter PRECISION = " + str(precision) + ";", 1 ) 
   write_line( f, "" )
   write_line( f, "input clk;", 1 ) 
   write_line( f, "input rst;", 1 ) 
   write_line( f, "input in;", 1 ) 
   write_line( f, "input last", 1 ) 
   write_line( f, "output [PRECISION-1:0] out", 1 ) 
   write_line( f, "" )
   write_line( f, "reg [PRECISION-1:0] count;", 1 ) 
   write_line( f, "" )
   write_line( f, "always @ (posedge clk) begin", 1 ) 
   write_line( f, "if (rst == 1 || last == 1) begin", 2 ) 
   write_line( f, "count <= 0;", 3 ) 
   write_line( f, "end", 2 ) 
   write_line( f, "else begin", 2 ) 
   write_line( f, "count <= count + in;", 3 ) 
   write_line( f, "end", 2 ) 
   write_line( f, "end", 1 ) 
   write_line( f, "" )
   write_line( f, "assign out = count;", 1 ) 
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

def write_header_sd_converter( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The module represents a stochastic to digital converter." )
   write_line( f, "// The input 'last' is used to choose the final length of the stochastic bitstreams" )
   write_line( f, "// when converting back to standard digital." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )
