# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains functions to generate testbenches for the modules
# produced by the top-level script, generate.py.

import numpy as np
from common import *
from pysc.linear_algebra.sc_dot_product import *
from pysc.rngs.lfsr import *
from pysc.core.arithmetic import *
import os
import random

# dot product testbench constants
_DP_DATA_FN = "data_vectors.mif"
_DP_WEIGHT_FN = "weight_vectors.mif"
_DP_SELECT_FN = "select_streams.mif"
_DP_RES_FN = "dp_results.mif"    
_DP_TEST_SIZE = 100

# matrix multiply testbench constants
_MM_INPUT_FN = "input_matrices.mif"
_MM_WEIGHT_FN = "weight_matrices.mif"
_MM_SEL_FN = "mm_select_streams.mif"
_MM_RES_FN = "mm_result.mif"
_MM_TEST_SIZE = 100

# alaghi adder testbench constants
_ALAGHI_INPUT_FN = "adder_inputs.mif"
_ALAGHI_RES_FN = "adder_results.mif"
_ALAGHI_TEST_SIZE = 100

# Main function for this module, involes the generation of all testbenches
# for the verilog modules generated by the top-level script. 
# This function creates and writes into a directory titled, 'tb'.
def generate( args ):
   M = args.batch_size
   N = args.input_size
   O = args.output_size 

   # if a module name is supplied, concatenate module names
   mm_tb_name = MATRIX + "_tb"
   mm_dut_name = MATRIX
   dp_tb_name = DOT_PROD + "_tb"
   dp_dut_name = DOT_PROD

   # make a folder for the testbenches called 'tb'
   # make a folder call 'data' within 'tb'
   tb = args.dest_dir + "/tb"
   if not os.path.exists( tb ):
      os.makedirs( tb )
   data = tb + "/data"
   if not os.path.exists( data ):
      os.makedirs( data )
 
   # write the matrix multiply testbench
   gen_mm_data( data, M, N, O, _MM_TEST_SIZE, rep=args.rep, alaghi=args.alaghi )
   with open( os.path.join( tb, mm_tb_name + ".v" ), 'w' ) as f:
      write_mm_tb( f, mm_tb_name, mm_dut_name, M, N, O, alaghi=args.alaghi )

   # write the dot product testbench
   gen_dp_data( data, N, _DP_TEST_SIZE, rep=args.rep, alaghi=args.alaghi )
   with open( os.path.join( tb, dp_tb_name + ".v" ), 'w' ) as f:
      write_dp_tb( f, dp_tb_name, dp_dut_name, N, rep=args.rep, alaghi=args.alaghi )

   if args.alaghi:
      alaghi_tb_name = ALAGHI_NADDER + "_tb"

      # write the alaghi adder testbench module
      gen_alaghi_data( data, N, _ALAGHI_TEST_SIZE )
      with open( os.path.join( tb, alaghi_tb_name + ".v" ), 'w' ) as f:
         write_alaghi_nadder_tb( f, alaghi_tb_name, args.input_size )
   else:
      nadder_tb_name = NADDER + "_tb"
      nadder_dut_name = NADDER

      # write the nadder testbench module
      with open( os.path.join( tb, nadder_tb_name + ".v" ), 'w' ) as f:
         write_nadder_tb( f, nadder_tb_name, nadder_dut_name, N )

# Writes the testbench module for the generated sc_matrix_multiply module.
# Parameters:
# f, file to write to 
# module_name, a string, name of the testbench
# dut_name, a string the module to test
# batch, an int, specifies batch size (in a matrix mult MxN * NxO, M is batch size)
# inpt, an int, specifies input feature size (N)
# outpt, an int, specifies output feature size (O)
def write_mm_tb( f, module_name, dut_name, batch, inpt, outpt, alaghi=False ):
   # write header comment
   write_mm_tb_header( f )
   
   # compute number of select streams needed 
   select_width = clogb2( inpt )

   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter BATCH_SIZE =      " + str(batch) + "; // M", 1 )
   write_line( f, "parameter INPUT_FEATURES =  " + str(inpt) + "; // N", 1 ) 
   write_line( f, "parameter OUTPUT_FEATURES = " + str(outpt) + "; // O", 1 )
   if not alaghi:
      write_line( f, "parameter SELECT_WIDTH =    " + str(select_width) + ";", 1 )
   write_line( f, "parameter INPUT_MATRICES =  \"" + _MM_INPUT_FN + "\";", 1 )
   write_line( f, "parameter WEIGHT_MATRICES = \"" + _MM_WEIGHT_FN + "\";", 1 )
   if not alaghi:
      write_line( f, "parameter SELECT_STREAM =   \"" + _MM_SEL_FN + "\";", 1 )
   write_line( f, "parameter MM_RESULT =       \"" + _MM_RES_FN + "\";", 1 )
   write_line( f, "parameter LENGTH =       " + str(_MM_TEST_SIZE) + ";", 1 )
   write_line( f, "" )
   write_line( f, "// module inputs and outputs", 1 )
   write_line( f, "reg clk;", 1 )
   write_line( f, "reg rst;", 1 )
   write_line( f, "wire [BATCH_SIZE*INPUT_FEATURES-1:0] inputStreams;", 1 )
   write_line( f, "wire [OUTPUT_FEATURES*INPUT_FEATURES-1:0] weightStreams;", 1 )
   if not alaghi:
      write_line( f, "wire [SELECT_WIDTH-1:0]                 sel;", 1 )
   write_line( f, "wire [BATCH_SIZE*OUTPUT_FEATURES-1:0]    outputStreams;", 1 )
   write_line( f, "wire                                     outputWriteEn;", 1 )
   write_line( f, "" )
   write_line( f, "// read input data and expected output data", 1 )
   write_line( f, "reg [BATCH_SIZE*INPUT_FEATURES-1:0] test_input [LENGTH-1:0];", 1 )
   write_line( f, "reg [OUTPUT_FEATURES*INPUT_FEATURES-1:0] test_weight [LENGTH-1:0];", 1 )
   if not alaghi:
      write_line( f, "reg [SELECT_WIDTH-1:0]                 test_sel [LENGTH-1:0];", 1 )
   write_line( f, "reg [BATCH_SIZE*OUTPUT_FEATURES-1:0] expected_results [LENGTH-1:0];", 1 )
   write_line( f, "initial begin", 1 )
   write_line( f, "$readmemb(INPUT_MATRICES, test_input, 0, LENGTH-1);", 2 )
   write_line( f, "$readmemb(WEIGHT_MATRICES, test_weight, 0, LENGTH-1);", 2 )
   if not alaghi:
      write_line( f, "$readmemb(SELECT_STREAM, test_sel, 0, LENGTH-1);", 2 )
   write_line( f, "$readmemb(MM_RESULT, expected_results, 0, LENGTH-1);", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "// Test input assignment logic", 1 )

   test_width = clogb2( _MM_TEST_SIZE )

   write_line( f, "reg [" + str(test_width-1) + ":0] test_index;", 1 )
   write_line( f, "initial test_index = 0;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst == 1'b1 ) begin", 2 )
   write_line( f, "test_index <= 0;", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "test_index <= test_index + 1;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "assign inputStreams = test_input[test_index];", 1 )
   write_line( f, "assign weightStreams = test_weight[test_index];", 1 )
   if not alaghi:
      write_line( f, "assign sel = test_sel[test_index];", 1 )
   write_line( f, "" )
   write_line( f, "// output checking and error handling", 1 )
   write_line( f, "integer result_index;", 1 )
   write_line( f, "integer errors;", 1 )
   write_line( f, "initial result_index = 0;", 1 )
   write_line( f, "initial errors = 0;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst ) begin", 2 )
   write_line( f, "result_index <= 0;", 3 )
   write_line( f, "end else if( outputWriteEn == 1'b1 ) begin", 2 )
   write_line( f, "if( outputStreams != expected_results[result_index] ) begin", 3 )
   write_line( f, "$display(\"Error. Expected result %B does not match actual %B. On result index: %d\",", 4 )
   write_line( f, "expected_results[result_index], outputStreams, result_index);", 5 )
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
   write_line( f, dut_name + " dut(", 1 )
   write_line( f, "clk,", 2 )
   write_line( f, "rst,", 2 )
   write_line( f, "inputStreams,", 2 )
   write_line( f, "weightStreams,", 2 )
   if not alaghi:
      write_line( f, "sel,", 2 )
   write_line( f, "outputStreams,", 2 )
   write_line( f, "outputWriteEn", 2 )
   write_line( f, ");", 1 )
   write_line( f, "" )
   write_line( f, "initial begin", 1 )
   write_line( f, "rst = 1;", 2 )
   write_line( f, "#(8*CLOCK_PERIOD);", 2 )
   write_line( f, "" )
   write_line( f, "// start sim", 2 )
   write_line( f, "rst = 0;", 2 )
   write_line( f, "#(LENGTH*CLOCK_PERIOD + 100)  // give 100 clock cycles for initial output delay", 2 )
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
   write_line( f, "endmodule // " + module_name )

   return

# Writes the testbench module for the generated sc_dot_product.
# Parameters:
#  f, the file to write to
#  module_name, a string, the name of the module
#  dut_name, a string, the name of the module to test (device under test)
#  rep, a string specifying the stochastic representation (either uni or bi)
#  length, an integer, the length of the input vectors
def write_dp_tb( f, module_name, dut_name, dimension, rep = "uni", alaghi = False ):
   # write the header comment
   write_dp_tb_header( f )

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
   write_line( f, dut_name + " dut(", 1 )
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

# Writes a testbench module for the generated sc_nadder.
# Parameter:
#  f, the file to write to
#  module_name, the name of the testbench module
#  dut_name, a string, the module to test
#  n, an int, the number of inputs to the nadder
def write_nadder_tb( f, module_name, dut_name, n ):
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
   write_line( f, dut_name + " dut(.x(x), .sel(sel), .out(out));", 1 )
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

def write_alaghi_nadder_tb( f, module_name, n ):
   # write the header comment
   write_alaghi_nadder_tb_header( f )

   delay = int(clogb2( n )) - 1

   write_line( f, "`timescale 1ns / 10ps" )
   write_line( f, "" )
   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter INPUT_STREAMS = " + str(n) + ";", 1 )
   write_line( f, "parameter DELAY =         " + str(delay) + ";", 1 )
   write_line( f, "parameter INPUTS =        \"" + _ALAGHI_INPUT_FN + "\";", 1 )
   write_line( f, "parameter ADDER_RESULT =  \"" + _ALAGHI_RES_FN + "\";", 1 )
   write_line( f, "parameter TEST_LENGTH =   " + str(_ALAGHI_TEST_SIZE) + ";", 1 )
   write_line( f, "" )
   write_line( f, "// modules inputs and outputs", 1 )
   write_line( f, "reg                      clk;", 1 )
   write_line( f, "reg                      rst;", 1 )
   write_line( f, "wire [INPUT_STREAMS-1:0] inpts;", 1 )
   write_line( f, "wire                     out;", 1 )
   write_line( f, "" )
   write_line( f, "// read input data and expected results data", 1 )
   write_line( f, "reg [INPUT_STREAMS-1:0] test_inputs [TEST_LENGTH-1:0];", 1 )
   write_line( f, "reg expected_results [TEST_LENGTH-1:0];", 1 )
   write_line( f, "initial begin", 1 )
   write_line( f, "$readmemb(INPUTS, test_inputs, 0, TEST_LENGTH-1);", 2 )
   write_line( f, "$readmemb(ADDER_RESULT, expected_results, 0, TEST_LENGTH-1);", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "// Test input data assignment logic", 1 )
   write_line( f, "reg [TEST_LENGTH-1:0] test_index;", 1 )
   write_line( f, "initial test_index = 0;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst == 1'b1 ) begin", 2 )
   write_line( f, "test_index <= 0;", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "test_index <= test_index + 1;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "assign inpts = test_inputs[test_index];", 1 )
   write_line( f, "" )
   write_line( f, "// Output checking and error handling", 1 )
   write_line( f, "reg valid;", 1 )
   write_line( f, "reg [TEST_LENGTH-1:0] valid_delay;", 1 )
   write_line( f, "initial valid_delay = 0;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst ) begin", 2 )
   write_line( f, "valid <= 0;", 3 )
   write_line( f, "valid_delay <= 0;", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "if( valid_delay == DELAY ) begin", 3 )
   write_line( f, "valid <= 1;", 4 )
   write_line( f, "end else begin", 3 )
   write_line( f, "valid_delay <= valid_delay + 1;", 4 )
   write_line( f, "end", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "integer result_index;", 1 )
   write_line( f, "integer errors;", 1 )
   write_line( f, "initial result_index = 0;", 1 )
   write_line( f, "initial errors = 0;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if( rst ) begin", 2 )
   write_line( f, "result_index <= 0;", 3 )
   write_line( f, "end else if( valid == 1'b1 ) begin", 2 )
   write_line( f, "if( out != expected_results[result_index] ) begin", 3 )
   write_line( f, "$display(\"Error. Expected result %d does not match actual %d. On result index: %d\",", 4 )
   write_line( f, "expected_results[result_index], out, result_index);", 5 )
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
   write_line( f, "alaghi_nadder dut(.clk(clk), .rst(rst), .inpts(inpts), .out(out));", 1 )
   write_line( f, "" )
   write_line( f, "initial begin", 1 )
   write_line( f, "// initialize inputs", 2 )
   write_line( f, "rst = 1;", 2 )
   write_line( f, "#(1*CLOCK_PERIOD);", 2 )
   write_line( f, "" )
   write_line( f, "// start sim", 2 )
   write_line( f, "rst = 0;", 2 )
   write_line( f, "#(TEST_LENGTH*CLOCK_PERIOD + 2*DELAY);", 2 )
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
   write_line( f, "endmodule // " + module_name )

# Write the header comment for the matrix multiply module to file, f.
def write_mm_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The module serves as a testbench for the stochastic matrix multiply" )
   write_line( f, "// module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )

# Write the header comment for the dot product testbench to file, f.
def write_dp_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The module serves as a testbench for the stochastic dot product module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )

# Writes the header comment for nadder testbench to file, f.
def write_nadder_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: This module serves as a testbench for the sc_nadder module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )

# Writes the header comment for alaghi_nadder testbench to file, f.
def write_alaghi_nadder_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: This module serves as a testbench for the alaghi_nadder module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )

# This function generates a few files used by the matrix multiply testbench.
# Files for input matrics, weight matrices, select streams and expected output
# are generated.
# Parameters:
#  data_dir, directory to write the data files into
#  batch, an int, batch size M  (in matrix multiply MxN *NxO)
#  inpt, an int, input feature size N
#  output, an int, output feature size O
#  length, an int, the length of the stochastic bit streams
#  rep, a string, 'uni' or 'bi', represents the type fo stochastic representation
#  alaghi, a boolean, 'True' specifies that alaghi adders are used
def gen_mm_data( data_dir, batch, inpt, outpt, length, rep="uni", alaghi=False ):
   # generate data/input features matrix
   datas = np.empty( (batch, inpt, length), dtype = bool )
   for b in range(batch):
      data = np.random.randint( length, size = inpt )
      rng = lfsr_sequence( length, normalize = False )   

      for i in range(inpt):
         datas[b, i, :] = rng < data[i]

   # generate weights matrix
   weights = np.empty( (outpt, inpt, length), dtype = bool )
   for o in range(outpt):
      weight = np.random.randint( length, size = inpt )
      rng = lfsr_sequence( length, normalize = False )

      for i in range(inpt):
         weights[o, i, :] = rng < weight[i]
   
   # write inputs and weights to data files
   with open( os.path.join( data_dir, _MM_INPUT_FN ), 'w' ) as f:
         write_matrix_stream( f, datas, length )
   with open( os.path.join( data_dir, _MM_WEIGHT_FN ), 'w' ) as f:
      write_matrix_stream( f, weights, length )

   results = np.empty( (batch, outpt, length), dtype = bool )
   if not alaghi:
      # generate a select stream
      sel_sequence = lfsr_sequence( length, normalize = False )
      
      # Write the select sequence out to a data file 
      with open( os.path.join( data_dir, _MM_SEL_FN ), 'w' ) as f:
         select_width = clogb2( inpt )
         for num in sel_sequence:
            sel = int(num % inpt)
            s_str = int_to_n_length_binary( sel, select_width ) 
            f.write( s_str + "\n" )

      # compute matrix multiply and write the results file
      for b in range(batch):
         data_vec = datas[b, :, :]
         for o in range(outpt):
            weight_vec = weights[o, :, :]
            res = sc_dot_product( data_vec, weight_vec, mode="LFSR", rep=rep, sel_sequence=sel_sequence )
            results[b, o, :] = res
   else:
      for b in range(batch):
         data_vec = datas[b, :, :]
         for o in range(outpt):
            weight_vec = weights[o, :, :]
            res = sc_dot_product( data_vec, weight_vec, mode="ALAGHI", rep=rep )
            results[b, o, :] = res

   with open( os.path.join( data_dir, _MM_RES_FN ), 'w' ) as f:
      write_matrix_stream( f, results, length )

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

# Function to generate random input data for the alaghi adder.
# Parameters:
#  data_dir, the directory to write the files into
#  n, an int, the number of inputs to the adder
#  length, an int, the length of the stochastic streams
def gen_alaghi_data( data_dir, n, length ):
   # generate a random vector of size n
   inpt = np.random.randint( length, size = n )
   rng = lfsr_sequence( length, normalize = False )
   inputs = np.empty( (n, length), dtype = bool )
   for d in range(n):
      inputs[d, :] = rng < inpt[d]

   # Write the input data to a file
   with open( os.path.join( data_dir, _ALAGHI_INPUT_FN ), 'w' ) as f:
      for stream in range(length):
         s_str = stream_to_str( inputs[:,stream] )
         f.write( s_str + "\n" )

   # compute the result and write them to a file
   result = alaghi_adder( inputs, n, length )
   with open( os.path.join( data_dir, _ALAGHI_RES_FN ), 'w' ) as f:
      for res in result:
         if res:
            res_str = "1"
         else:
            res_str = "0"
         f.write( res_str + "\n" )

# Takes in an array of 1's and 0's and outputs a string of
# those 1's and 0's concatenated.
def stream_to_str( stream, reverse = False ):
   s_str = ""
   for bit in stream:
      if bit:
         s_str = s_str + "1"
      else:
         s_str = s_str + "0"

   return s_str

# Converts a number, num, to a binary string of precision n.
def int_to_n_length_binary( num, n ):
   b_str = bin(num)[2:]
   for i in range(0, n - len(b_str)):
      b_str = "0" + b_str

   return b_str

# Writes a flattened form of the matrix (elements are streams of 1s and 0s)
# to the file f. The length of the streams should be equal to 'length'.
def write_matrix_stream( f, mtrx, length ):
   # Note: we write the string in an order interpretable by
   # verilog's readmemb() function. 
   for stream_idx in range(length):
      m_str = ""
      for m in reversed(range(len(mtrx))):
         vector = mtrx[m]
         for n in reversed(range(len(vector))):
            el = vector[n]
            if el[stream_idx]:
               m_str += "1"
            else:
               m_str += "0"

      f.write( m_str + "\n" )

def alaghi_adder( inputs, dimensions, length ):
   dims = int(2 ** clogb2(dimensions))
   zero = np.zeros( length, dtype=bool )
   while dims > 1:
      x = 0
      while x in range(dims):
         op_a = zero if x > dimensions else inputs[x, :]
         op_b = zero if x+1 > dimensions else inputs[x+1, :]
         add_res = sc_add( op_a, op_b, select_mode = "ALAGHI" )
         if x == 0:
            inputs[0, :] = add_res
         else:
            inputs[x/2, :] = add_res
         x = x + 2

      dims = dims / 2

   return inputs[0, :]
