# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains a function to generate a stochastic nadder module.

from common import *
import os

# Opens and writes a stochastic n-adder module to a file.
#  dest, a string, the directory to write the file to
#  n, an int, the number of inputs to the adder 
def generate( dest, n, test = True ):
   with open( os.path.join( dest, NADDER + ".v" ), 'w' ) as f:
      write_header_nadder( f )
      write_nadder_module( f, NADDER, n )

   if test:
      (tb, _) = makeTestDir( dest )
      tb_name = NADDER + "_tb"

      # write the nadder testbench module
      with open( os.path.join( tb, tb_name + ".v" ), 'w' ) as f:
         write_nadder_tb( f, tb_name, n )

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

# Writes a testbench module for the generated sc_nadder.
# Parameter:
#  f, the file to write to
#  module_name, the name of the testbench module
#  dut_name, a string, the module to test
#  n, an int, the number of inputs to the nadder
def write_nadder_tb( f, module_name, n ):
   # write the header comment
   write_nadder_tb_header( f ) 

   # compute number of select streams needed 
   select_width = clogb2( n ) 

   # compute the max possible number of input stream permutations
   # and select stream permutations
   input_count = int(math.pow( 2, n ))
   select_count = int(math.pow( 2, select_width ))

   write_line( f, "`timescale 1ns / 10ps" )
   write_line( f, "" )
   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter INPUT_STREAMS = " + str(n) + ";", 1 ) 
   write_line( f, "parameter SELECT_WIDTH = " + str(select_width) + ";", 1 ) 
   write_line( f, "" )
   write_line( f, "reg [INPUT_STREAMS-1:0] x;", 1 ) 
   write_line( f, "reg [SELECT_WIDTH-1:0]  sel;", 1 ) 
   write_line( f, "wire                    out;", 1 ) 
   write_line( f, "" )
   write_line( f, NADDER + " dut(.x(x), .sel(sel), .out(out));", 1 ) 
   write_line( f, "" )
   write_line( f, "integer errors;", 1 ) 
   write_line( f, "initial errors = 0;", 1 ) 
   write_line( f, "" )
   write_line( f, "integer i;", 1 ) 
   write_line( f, "integer s;", 1 ) 
   write_line( f, "initial begin", 1 ) 
   write_line( f, "// initialize inputs", 2 ) 
   write_line( f, "x = 0;", 2 ) 
   write_line( f, "sel = 0;", 2 ) 
   write_line( f, "#25;", 2 ) 
   write_line( f, "" )
   write_line( f, "// for all input stream permutations, test each possible select permutation", 2 ) 
   write_line( f, "for(i = 0; i < " + str(input_count) + "; i = i + 1) begin", 2 )
   write_line( f, "x = i;", 3 )
   write_line( f, "for(s = 0; s < " + str(select_count) + "; s = s + 1) begin", 3 )
   write_line( f, "sel = s;", 4 )
   write_line( f, "#5;", 4 )
   write_line( f, "if( x[s] != out ) begin", 4 )
   write_line( f, "$display( \"Error incorrect output. Input streams: %B, Select streams: %B, out: %d\", x, sel, out );", 5 )
   write_line( f, "errors = errors + 1;", 5 )
   write_line( f, "end", 4 )
   write_line( f, "#5;", 4 ) 
   write_line( f, "end", 3 ) 
   write_line( f, "end", 2 ) 
   write_line( f, "" )
   write_line( f, "// error summary", 2 )
   write_line( f, "if( errors > 0 ) begin", 2 )
   write_line( f, "$display(\"Validataion failure: %d error(s).\", errors);", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "$display(\"Validation successful.\");", 3 )
   write_line( f, "end", 2 )
   write_line( f, "" )
   write_line( f, "$stop;", 2 )
   write_line( f, "end", 1 )
   write_line( f, "endmodule // sc_nadder_tb" )

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

# Writes the header comment for nadder testbench to file, f.
def write_nadder_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: This module serves as a testbench for the sc_nadder module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
