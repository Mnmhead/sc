# Copyright (c) Gyorgy Wyatt Muntean 2017
# Python script to generate a Verilog LFSR module.

from common import *
import os

# Function to open and write a lfsr verilog module to a file.
#  dest, the directory to write the file into
#  length, the bit width of the LFSR's output
def generate( dest, length ):
   with open( os.path.join( dest, LFSR + ".v" ), 'w' ) as f:
      write_header_lfsr( f ) 
      write_lfsr_module( f, LFSR, length, zero_detect=True )

# Writes an LFSR module.
# Parameters:
#  f, the file to write to
#  module_name, a string
#  data_len, the bit width of the LFSR's output
#  zero_detect, a boolean, artificially adds a 0 value to the LFSR
#      zero_detect defaults to True
def write_lfsr_module( f, module_name, data_len, zero_detect=True ):
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
   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter N = " + str(data_len) + ";", 1 ) 
   write_line( f, "" )
   write_line( f, "input clk;", 1 ) 
   write_line( f, "input rst;", 1 ) 
   write_line( f, "input [N-1:0] seed;", 1 ) 
   write_line( f, "input enable;", 1 ) 
   write_line( f, "input restart;", 1 ) 
   write_line( f, "output [N-1:0] out;", 1 ) 
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
   for tap in taps:
      taps_str += " ^ shift_reg[" + str(tap) + "]"
   taps_str += ";"

   write_line( f, "wire xor_out;", 1 )
   write_line( f, "assign xor_out = " + taps_str, 1 )

   if zero_detect:
      write_line( f, "" )
      write_line( f, "wire zero_detector;", 1 )
      write_line( f, "assign zero_detector = ~(|(shift_reg[38:0]));", 1 )
      write_line( f, "assign shift_in = xout_out ^ zero_detector;", 1 )
      write_line( f, "" )

   write_line( f, "assign out = shift_reg;", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

# writes header comment for lfsr module
def write_header_lfsr( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a linear feedback shift register." )
   write_line( f, "// XOR tap locations have been taken from https://github.com/arminalaghi" )
   write_line( f, "// /scsynth/blob/master/src/VerilogLFSRGenerator.m" )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

