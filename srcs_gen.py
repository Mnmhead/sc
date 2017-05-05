# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains functions to generate basic modules
# needed to build the top level matrix multiply module.
# Modules like LFSR, Shift Register, etc are generated here.

from common import *
import os

# Generates all modules. Takes in user arguments
# which specifiy some module features.
def generate( args ):
   # make shift register for dot_products adder step
   shift = 2
   if( args.alaghi ):
      shift = 0 # Ill have to figure out how much delay there will be for alaghi adder trees

   shift_name = "shift_" + str(shift) + "_register"
   if args.module_name is not "":
      shift_name += "_" + args.module_name

   with open( os.path.join( args.dest_dir, shift_name + ".v" ), 'w' ) as f:
      write_shift_register_module( f, shift_name, shift )

   return

# Writes a counter module.
# Parameters:
#  f, file to write to
#  module_name, a string for module_name
#  max_num, 
def write_counter_module( f, module_name, max_num, reverse ):
   # write the header comment
   #write_header_counter( f )

   #write_line
   pass

def write_lfsr_module( f, module_name, max_num ):
   pass

# Writes a shift_n_register module. This module shifts a 1 bit value for n clock cycles.
# Parameters:
#  f, the file to write to
#  module_name, string for module name
#  shift, an int specifying how many clock cycles to shift for
def write_shift_register_module( f, module_name, shift ):
   # write the header comment
   write_header_shiftreg( f )

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

   return

# Writes the header comment for the shift_register module to file, f.
def write_header_shiftreg( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a 1-bit width shift register." )
   write_line( f, "// Shift depth is in the title of the module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )

   return

