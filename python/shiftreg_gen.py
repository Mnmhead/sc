# Copyright (c) Gyorgy Wyatt Muntean 2017
# Python script to generate a Verilog 1-bit shift-register module.
# Shifts by n cycles (n registers).

from common import *
import os

# Function to open and write a shift register verilog module to a file.
#  dest, the directory to write the file into
#  n, the number of registers in this shift register (i.e. the number of cycles to shift)
def generate( dest, n ):
   with open( os.path.join( dest, shiftreg_name( n ) + ".v" ), 'w' ) as f:
      write_header_shiftreg( f ) 
      write_shiftreg_module( f, shiftreg_name( n ), n )

# Writes a shift_n_register module. This module shifts a 1 bit value for n clock cycles.
# Parameters:
#  f, the file to write to
#  module_name, string for module name
#  shift, an int specifying how many clock cycles to shift for
def write_shiftreg_module( f, module_name, shift ):
   write_line( f, " module " + module_name + "(" )
   write_line( f, "input clk,", 1 ) 
   write_line( f, "input rst,", 1 ) 
   write_line( f, "input data_in,", 1 ) 
   write_line( f, "output data_out", 1 ) 
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter DEPTH = " + str(shift) + ";", 1 ) 
   write_line( f, "" )
   write_line( f, "reg internal_registers [DEPTH-1:0];", 1 ) 
   write_line( f, "" )
   write_line( f, "// assign first register", 1 ) 
   write_line( f, "always @ (posedge clk) begin", 1 ) 
   write_line( f, "if (rst == 1)", 2 ) 
   write_line( f, "internal_registers[0] <= 0;", 3 ) 
   write_line( f, "else", 2 ) 
   write_line( f, "internal_registers[0] <= data_in;", 3 ) 
   write_line( f, "end", 1 ) 
   write_line( f, "" )
   write_line( f, "genvar i;", 1 ) 
   write_line( f, "generate", 1 ) 
   write_line( f, "for (i = 1; i < DEPTH; i = i + 1) begin: sr_loop", 2 ) 
   write_line( f, "always @ (posedge clk) begin", 3 ) 
   write_line( f, "if (rst == 1)", 4 ) 
   write_line( f, "internal_registers[i] <= 0;", 5 ) 
   write_line( f, "else", 4 ) 
   write_line( f, "internal_registers[i] <= internal_registers[i-1];", 5 ) 
   write_line( f, "end", 3 ) 
   write_line( f, "end", 2 ) 
   write_line( f, "endgenerate", 1 ) 
   write_line( f, "" )
   write_line( f, "assign data_out = internal_registers[DEPTH-1];", 1 ) 
   write_line( f, "endmodule // shift_register" )

# Writes header for shift register module.
def write_header_shiftreg( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a 1-bit width shift register." )
   write_line( f, "// Shift depth is in the title of the module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

