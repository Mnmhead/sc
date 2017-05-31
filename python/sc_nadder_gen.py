# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains a function to generate a stochastic nadder module.

from common import *
import os

# Opens and writes a stochastic n-adder module to a file.
#  dest, a string, the directory to write the file to
#  n, an int, the number of inputs to the adder 
def generate( dest, n ):
   with open( os.path.join( dest, NADDER + ".v" ), 'w' ) as f:
      write_header_nadder( f )
      write_nadder_module( f, NADDER, n )

# Writes a sc_nadder module.
# Parameters:
#  f, the file to write to
#  module_name, a string for the module name
#  n, an integer which specifies the number of inputs to the adder module
def write_nadder_module( f, module_name, n ):
   # compute number of select streams needed
   select_width = clogb2( n )

   # write the header comment
   write_header_nadder( f )

   write_line( f, "module " + module_name + "(" )
   write_line( f, "x,", 1 )
   write_line( f, "sel,", 1 )
   write_line( f, "out", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter INPUT_STREAMS = " + str(n) + ";", 1 )
   write_line( f, "parameter SELECT_WIDTH = " + str(select_width) + ";", 1 )
   write_line( f, "" )
   write_line( f, "input [INPUT_STREAMS-1:0] x;", 1 )
   write_line( f, "input [SELECT_WIDTH-1:0]  sel;", 1 )
   write_line( f, "output                    out;", 1 )
   write_line( f, "" )
   write_line( f, "assign out = x[sel];", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

# Writes the header comment for the sc_nadder module.
# The file written to is the parameter, f.
def write_header_nadder( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a multi-input adder in the stochastic" )
   write_line( f, "// domain." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

