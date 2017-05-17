# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains functions to generate testbenches for the modules
# produced by the top-level script, generate.py.

from common import *
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
   nadder_tb_name = NADDER + "_tb"
   nadder_dut_name = NADDER

   # make a folder for the testbenches called 'tb'
   # make a folder call 'data' within 'tb'
   tb = args.dest_dir + "/tb"
   if not os.path.exists( tb ):
      os.makedirs( tb )
   data = tb + "/data"
   if not os.path.exists( data ):
      os.makedirs( data )
 
   # write the matrix multiply testbench
   gen_mm_data( data, M, N, O, args.rep )
   with open( os.path.join( tb, mm_tb_name + ".v" ), 'w' ) as f:
      write_mm_tb( f, mm_tb_name, mm_dut_name, M, N, O ) 

   # write the dot product testbench
   gen_dp_data( data, N, args.rep )
   with open( os.path.join( tb, dp_tb_name + ".v" ), 'w' ) as f:
      write_dp_tb( f, dp_tb_name, dp_dut_name, args.rep, N )

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
def write_mm_tb( f, module_name, dut_name, batch, inpt, outpt ):
   # write header comment
   write_mm_tb_header( f )
   
   # compute number of select streams needed 
   select_width = clogb2( inpt )

   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter BATCH_SIZE =      " + str(batch) + "; // M", 1 )
   write_line( f, "parameter INPUT_FEATURES =  " + str(inpt) + "; // N", 1 ) 
   write_line( f, "parameter OUTPUT_FEATURES = " + str(outpt) + "; // O", 1 )
   write_line( f, "parameter SELECT_WIDTH =    " + str(select_width) + ";", 1 )
   write_line( f, "parameter INPUT_MATRICES =  \"" + _MM_INPUT_FN + "\";", 1 )
   write_line( f, "parameter WEIGHT_MATRICES = \"" + _MM_WEIGHT_FN + "\";", 1 )
   write_line( f, "parameter SELECT_STREAM =   \"" + _MM_SEL_FN + "\";", 1 )
   write_line( f, "parameter MM_RESULT =       \"" + _MM_RES_FN + "\";", 1 )
   write_line( f, "parameter TEST_SIZE =       " + str(_MM_TEST_SIZE) + ";", 1 )
   write_line( f, "" )
   write_line( f, "// module inputs and outputs", 1 )
   write_line( f, "reg clk;", 1 )
   write_line( f, "reg rst;", 1 )
   write_line( f, "wire [BATCH_SIZE*INPUT_FEATURES-1:0] inputStreams;", 1 )
   write_line( f, "wire [OUTPUT_FEATURES*INPUT_FEATURES-1:0] weightStreams;", 1 )
   write_line( f, "wire [SELECT_WIDTH-1:0]                 sel;", 1 )
   write_line( f, "wire [BATCH_SIZE*OUTPUT_FEATURES-1:0]    outputStreams;", 1 )
   write_line( f, "wire                                     outputWriteEn;", 1 )
   write_line( f, "" )
   write_line( f, "// read input data and expected output data", 1 )
   write_line( f, "reg [BATCH_SIZE*INPUT_FEATURES-1:0] test_input [TEST_SIZE-1:0];", 1 )
   write_line( f, "reg [OUTPUT_FEATURES*INPUT_FEATURES-1:0] test_weight [TEST_SIZE-1:0];", 1 )
   write_line( f, "reg [SELECT_WIDTH-1:0]                 test_sel [TEST_SIZE-1:0];", 1 )
   write_line( f, "reg [BATCH_SIZE*OUTPUT_FEATURES-1:0] expected_results [TEST_SIZE-1:0];", 1 )
   write_line( f, "initial begin", 1 )
   write_line( f, "$readmemb(INPUT_MATRICES, test_input, 0, TEST_SIZE-1);", 2 )
   write_line( f, "$readmemb(WEIGHT_MATRICES, test_weight, 0, TEST_SIZE-1);", 2 )
   write_line( f, "$readmemb(SELECT_STREAM, test_sel, 0, TEST_SIZE-1);", 2 )
   write_line( f, "$readmemb(MM_RESULT, expected_results, 0, TEST_SIZE-1);", 2 )
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
   write_line( f, "#(TEST_SIZE*CLOCK_PERIOD + 100)  // give 100 clock cycles for initial output delay", 2 )
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
def write_dp_tb( f, module_name, dut_name, rep, length ):
   # write the header comment
   write_dp_tb_header( f )

   # compute number of select streams needed 
   select_width = clogb2( length )

   write_line( f, "`timescale 1ns / 10ps" )
   write_line( f, "" )   
   write_line( f, "module " + module_name + "();" )
   write_line( f, "parameter LENGTH =        " + str(length) + ";", 1 )
   write_line( f, "parameter SELECT_WIDTH =  " + str(select_width) + ";", 1 )
   write_line( f, "parameter DATA_VECTOR =   \"" + _DP_DATA_FN + "\";", 1 )
   write_line( f, "parameter WEIGHT_VECTOR = \"" + _DP_WEIGHT_FN + "\";", 1 )
   write_line( f, "parameter SELECT_STREAM = \"" + _DP_SELECT_FN + "\";", 1 )
   write_line( f, "parameter DP_RESULT =     \"" + _DP_RES_FN + "\";", 1 )
   write_line( f, "parameter TEST_SIZE =     " + str(_DP_TEST_SIZE) + ";", 1 )
   write_line( f, "" )
   write_line( f, "// module inputs and outputs", 1 )
   write_line( f, "reg                     clk;", 1 )
   write_line( f, "reg                     rst;", 1 )
   write_line( f, "wire [LENGTH-1:0]       data;", 1 )
   write_line( f, "wire [LENGTH-1:0]       weights;", 1 )
   write_line( f, "wire [SELECT_WIDTH-1:0] sel;", 1 )
   write_line( f, "wire                    result;", 1 )
   write_line( f, "wire                    valid;", 1 )
   write_line( f, "" )
   write_line( f, "// read input data and expected output data", 1 )
   write_line( f, "reg [LENGTH-1:0] test_data [TEST_SIZE-1:0];  // i think this only needs to be clogb2 of TEST_SIZE", 1 )
   write_line( f, "reg [LENGTH-1:0] test_weights [TEST_SIZE-1:0];", 1 )
   write_line( f, "reg [SELECT_WIDTH-1:0] test_sel [TEST_SIZE-1:0];", 1 )
   write_line( f, "reg expected_result [TEST_SIZE-1:0];", 1 )
   write_line( f, "initial begin", 1 )
   write_line( f, "$readmemb(DATA_VECTOR, test_data, 0, TEST_SIZE-1);", 2 )
   write_line( f, "$readmemb(WEIGHT_VECTOR, test_weights, 0, TEST_SIZE-1);", 2 )
   write_line( f, "$readmemb(SELECT_STREAM, test_sel, 0, TEST_SIZE-1);", 2 )
   write_line( f, "$readmemb(DP_RESULT, expected_result, 0, TEST_SIZE-1);", 2 )
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
   write_line( f, "$display(\"Error. Expected result %d foes not match actual %d. On result index: %d\", ", 4 )
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
   write_line( f, "#(TEST_SIZE*CLOCK_PERIOD + 100) // add 100 extra cycles for initial ouput delay", 2 )
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

   return

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

   return

# Write the header comment for the matrix multiply module to file, f.
def write_mm_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The module serves as a testbench for the stochastic matrix multiply" )
   write_line( f, "// module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )

   return

# Write the header comment for the dot product testbench to file, f.
def write_dp_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The module serves as a testbench for the stochastic dot product module." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )

   return

# Writes the header comment for nadder testbench to file, f.
def write_nadder_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: This module serves as a testbench for the sc_nadder module." )
   write_line( f, "// For more information on stochastic computing: https://en.wikipedia.org/wiki/Stochastic_computing" )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )

# This function generates a few files used by the matrix multiply testbench.
# The files contain binary input data (and 1 file contains expected results in binary).
# Parameters:
#  data_dir, directory to write the data files into
#  batch, an int, batch size M  (in matrix multiply MxN *NxO)
#  inpt, an int, input feature size N
#  output, an int, output feature size O
def gen_mm_data( data_dir, batch, inpt, outpt, rep ):
   # compute the width of the select stream
   select_width = clogb2( inpt )

   input_matrices = [] # array of flattened (batch x inpt) matrices
   weight_matrices = [] # array of flattened, transposed (inpt x outpt) matrices
   select_streams = [] # a 1D array of select numbers 
   results = [] # an array of flattened result matrices (batch x outpt)

   # generate the select streams
   for i in range(0, _MM_TEST_SIZE):
      select_streams.append( random.randint( 0, inpt - 1 ) )

   # generate the input and weight matrices
   for i in range(0, _MM_TEST_SIZE):
      input_matrix = []
      for j in range(0, batch*inpt):
         input_matrix.append( random.randint( 0, 1 ) )
      input_matrices.append( input_matrix )      
 
      weight_matrix = []  
      for k in range(0, inpt*outpt):
         weight_matrix.append( random.randint( 0, 1 ) )
      weight_matrices.append( weight_matrix )

   # compute the expected result matrices
   for i in range(0, _MM_TEST_SIZE):
      result_matrix = []
      input_matrix = input_matrices[ i ]
      weight_matrix = weight_matrices[ i ]

      for m in range(0, batch):
         # slice a vector out of input matrix
         batch_vector = input_matrix[(m*inpt):((m+1)*inpt)]
         for o in range(0, outpt):
            # slice a vector out of the weight matrix
            output_vector = weight_matrix[(o*inpt):((o+1)*inpt)]
            dot_product = sc_dot_product( batch_vector, output_vector, select_streams[i], rep )
            result_matrix.append( dot_product )

      results.append( result_matrix )
         
   # write input, weights, select and results to data files 
   with open( os.path.join( data_dir, _MM_INPUT_FN ), 'w' ) as f:
      for matrix in input_matrices: 
         m_str = stream_to_str( matrix )
         f.write( m_str + "\n" )

   with open( os.path.join( data_dir, _MM_WEIGHT_FN ), 'w' ) as f:
      for matrix in weight_matrices: 
         m_str = stream_to_str( matrix )
         f.write( m_str + "\n" )

   with open( os.path.join( data_dir, _MM_SEL_FN ), 'w' ) as f:
      for sel in select_streams:
         s_str = int_to_n_length_binary( sel, select_width ) 
         f.write( s_str + "\n" )

   with open( os.path.join( data_dir, _MM_RES_FN ), 'w' ) as f:
      for matrix in results:
         m_str = stream_to_str( matrix )
         f.write( m_str + "\n" )

   return
          

# This function generates a few files used by the dot product testbench.
# The files generated contain binary data used as input vectors.
# A file containing the expected results is also generated.
# Parameters:
#  data_dir, the directory to write the data files into
#  rep, a string specifying the stochastic representation. Either 'uni' or 'bi'.
#  length, an int, the length of the input vectors
def gen_dp_data( data_dir, length, rep ):
   # compute the bit width of the select streams
   select_width = clogb2( length )

   data_streams = [] # 2D array, this is a list of 100 data streams
   weight_streams = [] # 2D array, list of 100 weight streams
   select_streams = [] # 1D array of select numbers (0->length-1)
   results = [] # a 1D array of results (single bits, 1 or 0)

   # generate data and weights and select stream
   for i in range(0, _DP_TEST_SIZE):
      datas = []
      weights = []
      for j in range(0, length):
         # generate bits randomly
         datas.append( random.randint( 0, 1 ) )
         weights.append( random.randint( 0, 1 ) )

      data_streams.append( datas )
      weight_streams.append( weights )
      select_streams.append( random.randint( 0, length - 1 ) )

   # generate the expected outputs
   for i in range(0, _DP_TEST_SIZE):
      res = sc_dot_product( data_streams[ i ], weight_streams[ i ], select_streams[ i ], rep )
      results.append( res )           

   # Open and write data to files 
   with open( os.path.join( data_dir, _DP_DATA_FN ), 'w' ) as f:
      for stream in data_streams:
         s_str = stream_to_str( stream )
         f.write( s_str + "\n" )

   with open( os.path.join( data_dir, _DP_WEIGHT_FN ), 'w' ) as f:
      for stream in weight_streams:
         s_str = stream_to_str( stream )
         f.write( s_str + "\n" )

   with open( os.path.join( data_dir, _DP_SELECT_FN ), 'w' ) as f:
      for stream in select_streams:
         s_str = int_to_n_length_binary( stream, select_width ) 
         f.write( s_str + "\n" )

   with open( os.path.join( data_dir, _DP_RES_FN ), 'w' ) as f:
      for result in results:
         res_str = str(result)
         f.write( res_str + "\n" )

   return


#--------Helper functions----------#
# Computes the stochastic dot product of the two vectors, data_vec and weight_vec.
# Parameters:
#  data_vec and weight_vec are arrays of 1's and 0's
#  sel, is an integer in the range of 0 to length-1, where length is size of vectors
def sc_dot_product( data_vec, weight_vec, sel, rep='uni' ):
   reverseIndex = len(data_vec) - 1 - sel
   if rep == 'uni':
      # uni polar multiplier is an AND gate
      return data_vec[reverseIndex] & weight_vec[reverseIndex]
   elif rep == 'bi':
      # bi polar multiplier is an XNOR gate
      xor = data_vec[reverseIndex] ^ weight_vec[reverseIndex]
      if xor == 1:
         return 0
      elif xor == 0:
         return 1

# Takes in an array of 1's and 0's and outputs a string of
# those 1's and 0's concatenated.
def stream_to_str( stream ):
   s_str = ""
   for bit in stream:
      s_str += str(bit)
        
   return s_str

# Converts a number, num, to a binary string of precision n.
def int_to_n_length_binary( num, n ):
   b_str = bin(num)[2:]
   for i in range(0, n - len(b_str)):
      b_str = "0" + b_str

   return b_str
