# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains a function to generate a Verilog module 
# for stochastic dot product.

import alaghi_nadder_gen
from common import *
import os
from pysc.linear_algebra.sc_dot_product import *
import sc_nadder_gen
import shiftreg_gen

# dot product testbench constants
_DP_DATA_FN = "data_vectors.mif"
_DP_WEIGHT_FN = "weight_vectors.mif"
_DP_SELECT_FN = "select_streams.mif"
_DP_RES_FN = "dp_results.mif"
_DP_TEST_SIZE = 100


# Opens and writes a stochastic dot product module to a file.
#  dest, a string, the directory to write the file into
#  dimensions, an int, the dimension of the vectors to dot-product 
#  rep, the stochastic representation
#  alaghi, a boolean, specifies if alaghi adder tree is used
def generate( dest, dimensions, rep = "uni", alaghi = False, test = True ):
   # generate the shift_register
   delay = None
   if alaghi:
      # delay for alaghi tree is one cycle for every level, plus one for
      # final output register of the alaghi adder and another for the final
      # register of the dot product.
      delay = int(clogb2( dimensions )) + 2
      alaghi_nadder_gen.generate( dest, dimensions ) 
   else:
      # two clock cycle delay for standard dot product
      # 1 cycle for multiplication, 1 for addition (single mux)
      delay = 2
      sc_nadder_gen.generate( dest, dimensions )      

   shiftreg_gen.generate( dest, delay )

   with open( os.path.join( dest, DOT_PROD + ".v" ), 'w' ) as f:
      write_header_dot_prod( f )
      write_dot_prod_module( f, DOT_PROD, dimensions, rep, alaghi )

   if test:
      (tb, data) = makeTestDir( dest )
      tb_name = DOT_PROD + "_tb"

      # write the dot product testbench
      gen_dp_data( data, dimensions, _DP_TEST_SIZE, rep="uni", alaghi=alaghi )
      with open( os.path.join( tb, tb_name + ".v" ), 'w' ) as f:
         # write the header comment
         write_dp_tb_header( f )
         write_dp_tb( f, tb_name, dimensions, rep="uni", alaghi=alaghi )


# Writes a stochastic dot_product module to the file, f.
# Parameters:
#  f, the file to write to
#  rep, a string for the stochastic represntation type (uni or bi)
#  module_name, a string for the module name
#  dimensions, an int which specifies the length of the input vectors to the module
def write_dot_prod_module( f, module_name, dimensions, rep = "uni", alaghi = False ):
   # compute number of select streams
   select_width = clogb2( dimensions )

   write_line( f, "module " + module_name + "(" )
   write_line( f, "clk,", 1 )
   write_line( f, "rst,", 1 )
   write_line( f, "data,", 1 )
   write_line( f, "weights,", 1 )
   if not alaghi:
      write_line( f, "sel,", 1 )
   write_line( f, "result,", 1 )
   write_line( f, "valid", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter LENGTH = " + str(dimensions) + ";", 1 )
   if not alaghi:
      write_line( f, "parameter SELECT_WIDTH = " + str(select_width) + ";", 1 )
   write_line( f, "" )
   write_line( f, "// inputs and outputs", 1 )
   write_line( f, "input                    clk;", 1 )
   write_line( f, "input                    rst;", 1 )
   write_line( f, "input [LENGTH-1:0]       data;", 1 )
   write_line( f, "input [LENGTH-1:0]       weights;", 1 )
   if not alaghi:
      write_line( f, "input [SELECT_WIDTH-1:0] sel;", 1 )
   write_line( f, "output                   result;", 1 )
   write_line( f, "output                   valid;", 1 )
   write_line( f, "" )
   write_line( f, "// multipication modules, for element wise multiplication of data and weights", 1 )
   write_line( f, "genvar i;", 1 )
   write_line( f, "wire [LENGTH-1:0] mult_out;", 1 )
   write_line( f, "generate", 1 )
   write_line( f, "for( i = 0; i < LENGTH; i = i + 1) begin : mult", 2 )
   if rep == 'uni':
      write_line( f, "sc_multiplier MULT(.x(data[i]), .y(weights[i]), .res(mult_out[i]));", 3 )
   if rep == 'bi':
      write_line( f, "sc_multiplier_bi MULT(.x(data[i]), .y(weights[i]), .z(mult_out[i]));", 3 )
   write_line( f, "end", 2 )
   write_line( f, "endgenerate", 1 )
   write_line( f, "" )
   write_line( f, "// direct multiplication output to an intermediate register", 1 )
   write_line( f, "reg [LENGTH-1:0] product_streams;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst == 1'b1 ) begin", 2 )
   write_line( f, "product_streams <= 0;", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "product_streams <= mult_out;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   if not alaghi:
      write_line( f, "// shift the slect streams by 1 cycle, must wait for multiplication to complete", 1 )
      write_line( f, "reg [SELECT_WIDTH-1:0] select;", 1 )
      write_line( f, "always @(posedge clk) begin", 1 )
      write_line( f, "if( rst == 1'b1 ) begin", 2 )
      write_line( f, "select <= 0;", 3 )
      write_line( f, "end else begin", 2 )
      write_line( f, "select <= sel;", 3 )
      write_line( f, "end", 2 )
      write_line( f, "end", 1 )
      write_line( f, "" )
   write_line( f, "// add all element-wise products", 1 )
   write_line( f, "wire adder_res;", 1 )
   if alaghi:
      write_line( f, "alaghi_nadder NADDER(.clk(clk), .rst(rst), .inpts(product_streams), .out(adder_res));", 1 )
   else:
      write_line( f, "sc_nadder NADDER(.x(product_streams), .sel(select), .out(adder_res));", 1 )
   write_line( f, "" )
   write_line( f, "// direct adder output to register and then to final output", 1 )
   write_line( f, "reg i_result;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst == 1'b1 ) begin", 2 )
   write_line( f, "i_result <= 0;", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "i_result <= adder_res;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "assign result = i_result;", 1 )
   write_line( f, "" )
   write_line( f, "// Use shift register to indicate when module output is valid", 1 )
   if alaghi:
      delay = int(clogb2( dimensions )) + 2
   else:
      delay = 2
   write_line( f, "shift_" + str(delay) + "_register SHIFT" + str(delay) \
                  + "(.clk(clk), .rst(rst), .data_in(1'b1), .data_out(valid));", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

# Writes the testbench module for the generated sc_dot_product.
# Parameters:
#  f, the file to write to
#  module_name, a string, the name of the module
#  rep, a string specifying the stochastic representation (either uni or bi)
#  length, an integer, the length of the input vectors
def write_dp_tb( f, module_name, dimension, rep = "uni", alaghi = False ):
     # compute number of select streams needed 
   select_width = clogb2( dimension )

   write_line( f, "`timescale 1ns / 10ps" )
   write_line( f, "" )
   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter DIMENSION =     " + str(dimension) + ";", 1 )
   if not alaghi:
      write_line( f, "parameter SELECT_WIDTH =  " + str(select_width) + ";", 1 )
   write_line( f, "parameter DATA_VECTOR =   \"" + _DP_DATA_FN + "\";", 1 )
   write_line( f, "parameter WEIGHT_VECTOR = \"" + _DP_WEIGHT_FN + "\";", 1 )
   write_line( f, "parameter SELECT_STREAM = \"" + _DP_SELECT_FN + "\";", 1 )
   write_line( f, "parameter DP_RESULT =     \"" + _DP_RES_FN + "\";", 1 )
   write_line( f, "parameter LENGTH =        " + str(_DP_TEST_SIZE) + ";", 1 )
   write_line( f, "" )
   write_line( f, "// module inputs and outputs", 1 )
   write_line( f, "reg                     clk;", 1 )
   write_line( f, "reg                     rst;", 1 )
   write_line( f, "wire [DIMENSION-1:0]    data;", 1 )
   write_line( f, "wire [DIMENSION-1:0]    weights;", 1 )
   if not alaghi:
      write_line( f, "wire [SELECT_WIDTH-1:0] sel;", 1 )
   write_line( f, "wire                    result;", 1 )
   write_line( f, "wire                    valid;", 1 )
   write_line( f, "" )
   write_line( f, "// read input data and expected output data", 1 )
   write_line( f, "reg [DIMENSION-1:0] test_data [LENGTH-1:0];", 1 )
   write_line( f, "reg [DIMENSION-1:0] test_weights [LENGTH-1:0];", 1 )
   if not alaghi:
      write_line( f, "reg [SELECT_WIDTH-1:0] test_sel [LENGTH-1:0];", 1 )
   write_line( f, "reg expected_result [LENGTH-1:0];", 1 )
   write_line( f, "initial begin", 1 )
   write_line( f, "$readmemb(DATA_VECTOR, test_data, 0, LENGTH-1);", 2 )
   write_line( f, "$readmemb(WEIGHT_VECTOR, test_weights, 0, LENGTH-1);", 2 )
   if not alaghi:
      write_line( f, "$readmemb(SELECT_STREAM, test_sel, 0, LENGTH-1);", 2 )
   write_line( f, "$readmemb(DP_RESULT, expected_result, 0, LENGTH-1);", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "// Test input assignment logic", 1 )

   test_width = clogb2( _DP_TEST_SIZE )

   write_line( f, "reg [" + str(test_width-1) + ":0] test_index;", 1 )
   write_line( f, "initial test_index = 0;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst == 1'b1 ) begin", 2 )
   write_line( f, "test_index <= 0;", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "test_index <= test_index + 1;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "assign data = test_data[test_index];", 1 )
   write_line( f, "assign weights = test_weights[test_index];", 1 )
   if not alaghi:
      write_line( f, "assign sel = test_sel[test_index];", 1 )
   write_line( f, "" )
   write_line( f, "// Output checking and error handling", 1 )
   write_line( f, "integer result_index;", 1 )
   write_line( f, "integer errors;", 1 )
   write_line( f, "initial result_index = 0;", 1 )
   write_line( f, "initial errors = 0;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst ) begin", 2 )
   write_line( f, "result_index <= 0;", 3 )
   write_line( f, "end else if( valid == 1'b1 ) begin", 2 )
   write_line( f, "if( result != expected_result[result_index] ) begin", 3 )
   write_line( f, "$display(\"Error. Expected result %d does not match actual %d. On result index: %d\", ", 4 )
   write_line( f, "expected_result[result_index], result, result_index);", 5 )
   write_line( f, "errors = errors + 1;", 4 )
   write_line( f, "end", 3 )
   write_line( f, "" )
   write_line( f, "result_index = result_index + 1;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "// Clock Generation", 1 )
   write_line( f, "parameter CLOCK_PERIOD=10;", 1 )
   write_line( f, "initial clk=1;", 1 )
   write_line( f, "always begin", 1 )
   write_line( f, "#(CLOCK_PERIOD/2);", 2 )
   write_line( f, "clk = ~clk;", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "// instantiate module", 1 )
   write_line( f, DOT_PROD + " dut(", 1 )
   write_line( f, ".clk(clk),", 2 )
   write_line( f, ".rst(rst),", 2 )
   write_line( f, ".data(data),", 2 )
   write_line( f, ".weights(weights),", 2 )
   if not alaghi:
      write_line( f, ".sel(sel),", 2 )
   write_line( f, ".result(result),", 2 )
   write_line( f, ".valid(valid)", 2 )
   write_line( f, ");", 1 )
   write_line( f, "" )
   write_line( f, "initial begin", 1 )
   write_line( f, "// initialize inputs", 2 )
   write_line( f, "rst = 1;", 2 )
   write_line( f, "#(8*CLOCK_PERIOD);", 2 )
   write_line( f, "" )
   write_line( f, "// start sim", 2 )
   write_line( f, "rst = 0;", 2 )
   write_line( f, "#(LENGTH*CLOCK_PERIOD + 100) // add 100 extra cycles for initial ouput delay", 2 )
   write_line( f, "" )
   write_line( f, "// error summary", 2 )
   write_line( f, "$display(\"Simulation complete.\");", 2 )
   write_line( f, "if( errors > 0 ) begin", 2 )
   write_line( f, "$display(\"Validataion failure: %d error(s).\", errors);", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "$display(\"Validation successful.\");", 3 )
   write_line( f, "end", 2 )
   write_line( f, "" )
   write_line( f, "$stop;", 2 )
   write_line( f, "end", 1 )
   write_line( f, "endmodule // sc_dot_product_tb" )

# This function generates a few files used by the dot product testbench.
# Files for input data vector, weight vector, select streams and final
# dot_product results are generated. 
#
# Parameters:
#  data_dir, the directory to write the 'mif' data files
#  dimension, an int, the dimension of the vectors
#  length, the length of the input streams (essentially the length of the test)
#  rep, a string, 'uni' or 'bi' specifying the stochastic representation
#  alaghi, a boolean, specifies whether alaghi adders are used in the dot_product
def gen_dp_data( data_dir, dimension, length, rep='uni', alaghi=False ):
   # randomly generate some data and weight vectors
   data = np.random.randint( length, size = dimension )
   weight = np.random.randint( length, size = dimension )

   rng0 = lfsr_sequence( length, normalize = False )
   rng1 = lfsr_sequence( length, normalize = False )

   datas = np.empty( (dimension, length), dtype = bool )
   weights = np.empty( (dimension, length), dtype = bool )

   for d in range(dimension):
      datas[d, :] = rng0 < data[d]
      weights[d, : ] = rng1 < weight[d]

   # Write the data and weight vectors out to 'mif' files
   # Open and write data to files 
   with open( os.path.join( data_dir, _DP_DATA_FN ), 'w' ) as f:
      for stream in range(length):
         s_str = stream_to_str( datas[:,stream] )
         f.write( s_str + "\n" )
   with open( os.path.join( data_dir, _DP_WEIGHT_FN ), 'w' ) as f:
      for stream in range(length):
         s_str = stream_to_str( weights[:,stream] )
         f.write( s_str + "\n" )

   if not alaghi:
      # generate a select stream
      sel_sequence = lfsr_sequence( length, normalize = False )

      # Write the select sequence out to a data file 
      with open( os.path.join( data_dir, _DP_SELECT_FN ), 'w' ) as f:
         select_width = clogb2( dimension )
         for num in sel_sequence:
            sel = int(num % dimension)
            s_str = int_to_n_length_binary( sel, select_width )
            f.write( s_str + "\n" )

      # compute the standard dot product
      result = sc_dot_product( datas, weights, mode="LFSR", rep=rep, sel_sequence=sel_sequence )
   else:
      result = sc_dot_product( datas, weights, mode="ALAGHI", rep=rep )

   # write out the dot_product result to a 'mif' file
   with open( os.path.join( data_dir, _DP_RES_FN ), 'w' ) as f:
      for res in result:
         if res:
            res_str = "1"
         else:
            res_str = "0"
         f.write( res_str + "\n" )

# Writes the header comment for the sc_dot_product module.
# The file written to is the parameter, f.
def write_header_dot_prod( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The circuit represents a dot product of two vectors in the" )
   write_line( f, "// stochastic domain." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

# Write the header comment for the dot product testbench to file, f.
def write_dp_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The module serves as a testbench for the stochastic dot product module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )

# Helper function
# Takes in an array of 1's and 0's and outputs a string of
# those 1's and 0's concatenated.
# Characters of the stream are concatenated to the front,
# this is because we write the stream to the data file
# in a way that makes it easy for verilog's readmemb()
# to read the data.
def stream_to_str( stream, reverse = False ):
   s_str = ""
   for bit in stream:
      #s_str = "1" + s_str if bit else "0" + s_str
      if bit:
         s_str = "1" + s_str
      else:
         s_str = "0" + s_str

   return s_str

# Helper function
# Converts a number, num, to a binary string of precision n. 
def int_to_n_length_binary( num, n ): 
   b_str = bin(num)[2:] 
   for i in range(0, n - len(b_str)): 
      b_str = "0" + b_str 
 
   return b_str



generate( "l", 90 )
