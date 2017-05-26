# Copyright (c) Gyorgy Wyatt Muntean 2017
# Python script to generate a Verilog counter module.

from common import *
import os

# Function to open and write a modular counter verilog module to a file.
#	dest, the directory to write the file into
#  threshold_value, max value this counter reaches (range is [0,threshold])
def generate( dest, threshold_value ):
	with open( os.path.join( dest, COUNTER + ".v" ), 'w' ) as f:
   	write_header_counter( f )
		write_modular_counter_module( f, COUNTER, threshold_value )

# Writes a counter module.
# Parameters:
#  f, file to write to
#  module_name, a string for module_name
#  width, an int, the bit_width of the counter
#  threshold, the number the counter reaches before it wraps back to 0 
# 		(output in range [0,max_num])
def write_modular_counter_module( f, module_name, threshold ):
   # calculate bit_width of the counter
   bit_width = clogb2( threshold )

   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter N = " + str(threshold) + ";", 1 )
   write_line( f, "" )
   write_line( f, "input clk;", 1 )
   write_line( f, "input rst;", 1 )
   write_line( f, "input enable;", 1 )
   write_line( f, "input restart;", 1 )
   write_line( f, "output [" + str(bit_width) + "-1:0] out", 1 )
   write_line( f, "" )
   write_line( f, "reg [" + str(bit_width) + "-1:0] counter;", 1 )
   write_line( f, "always @(posedge clk or posedge rst) begin", 1 )
   write_line( f, "if (rst) counter <= 0;", 2 )
   write_line( f, "else if (restart) counter <= 0;", 2 )
   write_line( f, "else if (enable) begin", 2 )
   write_line( f, "if (counter == N) counter <= 0;", 3 )
   write_line( f, "else counter <= counter + 1;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

# Writes comment for counter module.
def write_header_counter( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a counter which counts up to N" )
   write_line( f, "// and wraps back to 0." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

