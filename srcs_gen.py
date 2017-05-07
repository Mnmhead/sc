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

   """
   width = args.precision
   reverse = False
   with open( os.path.join( args.dest_dir, counter_name + ".v"), 'w' ) as f:
      write_counter_module( f, counter_name, width )
   """

   """
   data_len = args.precision
   with open( os.path.join( args.dest_dir, lfsr_name + ".v"), 'w' ) as f:
      write_lfsr_module( f, lfsr_name, data_len )
   """

   return

# Writes a counter module.
# Parameters:
#  f, file to write to
#  module_name, a string for module_name
#  width, an int, the bit_width of the counter
#  max_num, the number the counter reaches before it wraps back to 0 (counter's output is [0,max_num])
#      max_num defaults to 2^(width) - 1 .
#  reverse, an optional boolean which causes the output of the counter to be reversed
def write_counter_module( f, module_name, width, max_num=0, reverse=False ):
   # write the header comment
   write_header_counter( f )

   # calculate bit_width of the counter
   bit_width = clogb2( max_num )
   
   write_line( f, "module " + module_name + "(" )
   write_line( f, "clk,", 1 )
   write_line( f, "rst,", 1 )
   write_line( f, "enable,", 1 )
   write_line( f, "restart,", 1 )
   write_line( f, "out", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter N = " + str(bit_width) + ";", 1 )
   write_line( f, "parameter BOUND = " + str(max_num) + "; // the upper bound of the range of this counter", 1 )
   write_line( f, "" )
   write_line( f, "input clk;", 1 )
   write_line( f, "input rst;", 1 )
   write_line( f, "input enable;", 1 )
   write_line( f, "input restart;", 1 )
   write_line( f, "output [N-1:0] out", 1 )
   write_line( f, "" )
   write_line( f, "reg [N-1:0] counter;", 1 )
   write_line( f, "always @(posedge clk or posedge rst) begin", 1 )
   write_line( f, "if (rst) counter <= 0;", 2 )
   write_line( f, "else if (restart) counter <= 0;", 2 )
   write_line( f, "else if (enable) begin", 2 )
   write_line( f, "if (counter == BOUND) counter <= 0;", 3 )
   write_line( f, "else counter <= counter + 1;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )

   if reverse:
       write_line( f, "" )
       write_line( f, "genvar i;", 1 )
       write_line( f, "generate", 1 )
       write_line( f, "for(i=0; i<10;i=i+1) assign out[i] = counter[N-1-i];", 2 )
       write_line( f, "endgenerate", 1 )

   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )
 
   return

# Writes an LFSR module.
# Parameters:
#  f, the file to write to
#  module_name, a string 
#  data_len, the bit width of the LFSR's output
#  max_num, an int, the maximum number in decimal this LFSR will generate
#      max_num defaults to 2^(data_len) - 1
#  zero_detect, a boolean, artificially adds a 0 value to the LFSR
#      zero_detect defaults to True
def write_lfsr_module( f, module_name, data_len, max_num=0, zero_detect=True ):
   # write the header comment
   write_header_lfsr( f )

   # hard code the xor taps into a dictionary (bit_width->tapLocations)
   taps_dict = {}
   taps_dict[3] = [3, 2]
   taps_dict[4] = [4, 3]
   taps_dict[5] = [5, 3]
   taps_dict[6] = [6, 5]
   taps_dict[7] = [7, 6]
   taps_dict[8] = [8, 7, 6, 1]
   taps_dict[9] = [9, 5]
   taps_dict[10] = [10, 7]
   taps_dict[11] = [11, 9]
   taps_dict[12] = [12, 11, 10, 4]
   taps_dict[13] = [13, 12, 11, 8]
   taps_dict[14] = [14, 13, 12, 2]
   taps_dict[15] = [15, 14]
   taps_dict[16] = [16, 15, 13, 4]
   taps_dict[17] = [17, 14]
   taps_dict[18] = [18, 11]
   taps_dict[19] = [19, 18, 17, 14] 
   taps_dict[20] = [20, 17]
   taps_dict[24] = [24, 23, 22, 17]
   taps_dict[32] = [32, 31, 30, 10]

   # begin writing the module
   write_line( f, "module " + module_name + "(" )
   write_line( f, "clk,", 1 )
   write_line( f, "rst,", 1 )
   write_line( f, "seed,", 1 )
   write_line( f, "enable,", 1 )
   write_line( f, "restart,", 1 )
   write_line( f, "data", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter N = " + str(data_len) + ";" )
   write_line( f, "" )
   write_line( f, "input clk;", 1 )
   write_line( f, "input rst;", 1 )
   write_line( f, "input [N-1:0] seed;", 1 )
   write_line( f, "input enable;", 1 )
   write_line( f, "input restart;", 1 )
   write_line( f, "output [N-1:0] data;", 1 )
   write_line( f, "" )
   write_line( f, "reg [N-1:0] shift_reg;", 1 )
   write_line( f, "wire shift_in;", 1 )
   write_line( f, "" )
   write_line( f, "always @(posedge clk or pasedge rst) begin", 1 )
   write_line( f, "if (rst) shift_reg <= seed;", 2 )
   write_line( f, "else if (restart) shift_reg <= seed;", 2 )
   write_line( f, "else if (enable) shift_reg <= {shift_reg[N-2:0], shift_in};", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )

   # determine and place the xor taps
   taps = taps_dict.get( data_len )
   if( taps == None ):
      taps = [3, 2]
  
   # add the first tap, then delete it from list
   taps_str = "shift_reg[" + str(taps[0]) + "]"
   del taps[0]
   for i in range(0,taps):
      taps_str += " ^ shift_reg[" + str(taps[i]) + "]"
   taps_str += ";"

   write_line( f, "wire xor_out;", 1 )
   write_line( f, "assign xor_out = " + taps_str, 1 )

   if zero_detect:
      write_line( f, "" )
      write_line( f, "wire zero_detector;", 1 )
      write_line( f, "assign zero_detector = ~(|(shift_reg[38:0]));", 1 )
      write_line( f, "assign shift_in = xout_out ^ zero_detector;", 1 )
      write_line( f, "" )

   write_line( f, "assign data = shift_reg;", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

   return

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
   write_line( f, "" )

   return

# Writes the header comment for the counter module to file, f.
def write_header_counter( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a counter which counts up to BOUND" )
   write_line( f, "// and wraps back to 0." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

   return

def write_header_lfsr( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a linear feedback shift register." )
   write_line( f, "// XOR tap locations have been taken from https://github.com/arminalaghi" ) 
   write_line( f, "// /scsynth/blob/master/src/VerilogLFSRGenerator.m" )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

   return

