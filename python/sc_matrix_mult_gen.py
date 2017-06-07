# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains functions to generate the core modules for
# stochastic matrix multiply. 

from common import *
import numpy as np
import os
from pysc.core.arithmetic import *
from pysc.linear_algebra.sc_dot_product import *
from pysc.rngs.lfsr import *
import sc_dot_product_gen

# matrix multiply testbench constants
_MM_INPUT_FN = "input_matrices.mif"
_MM_WEIGHT_FN = "weight_matrices.mif"
_MM_SEL_FN = "mm_select_streams.mif"
_MM_RES_FN = "mm_result.mif"
_MM_TEST_SIZE = 100


# Generates a stochastic matrix multiply module and writes it to a file.
#  dest, a string, the directory to write the file to
#  batch, an int, batch size (M in MxN * N*O)
#  input_features, an int, N
#  output_features, an int, O
#  alaghi, boolean, specifies use of alaghi adders instead of conventional 
#     stochastic adders
def generate( dest, batch, input_features, output_features, alaghi = False, test = True ):
   M = batch
   N = input_features
   O = output_features

   # Generate the core of matrix multiply, the dot_prodcut module   
   sc_dot_product_gen.generate( dest, input_features, rep="uni", alaghi=alaghi )

   with open( os.path.join( dest, MATRIX + ".v" ), 'w' ) as f: 
      write_header_mat_mult( f )
      write_matrix_module( f, MATRIX, M, N, O, alaghi=alaghi )

   if test:
      # make the testbench directory 
      (tb, data) = makeTestDir( dest )	
      tb_name = MATRIX + "_tb"

      # write the matrix multiply testbench
      gen_mm_data( data, M, N, O, _MM_TEST_SIZE, rep="uni", alaghi=alaghi )
      with open( os.path.join( tb, tb_name + ".v" ), 'w' ) as f:
         # write header comment
         write_mm_tb_header( f ) 
         write_mm_tb( f, tb_name, M, N, O, alaghi=alaghi )

# Writes a stochatsic matrix multiply module to an output file, f.
# Parameters:
#  module_name, a string for the module
#  batch, an int specifying the batch size (in a matrix mult MxN * NxO, M is batch size)
#  inpt, an int specifying the input feature size (N)
#  outpt, an int specifying the output feature size (O)
def write_matrix_module( f, module_name, batch, inpt, outpt, alaghi = False ):
   # compute the log base 2 of the input, 
   # this is how many select streams are required
   select_width = clogb2( inpt )

   write_line( f, "module " + module_name + "(" )
   write_line( f, "clk,", 1 )
   write_line( f, "rst,", 1 )
   write_line( f, "inputStreams,", 1 )
   write_line( f, "weightStreams,", 1 )
   if not alaghi:
      write_line( f, "sel,", 1 )
   write_line( f, "outputStreams,", 1 )
   write_line( f, "outputWriteEn", 1 )
   write_line( f, ");" )
   write_line( f, "" )
   write_line( f, "parameter BATCH_SIZE = " + str(batch) + "; // M", 1 )
   write_line( f, "parameter INPUT_FEATURES = " + str(inpt) + "; // N", 1 )
   write_line( f, "parameter OUTPUT_FEATURES = " + str(outpt) + "; // O", 1 )
   if not alaghi:
      write_line( f, "parameter SELECT_WIDTH = " + str(select_width) + ";", 1 )
   write_line( f, "" )
   write_line( f, "// inputs and outputs", 1 )
   write_line( f, "input                                      clk;", 1 )
   write_line( f, "input                                      rst;", 1 )
   write_line( f, "input [BATCH_SIZE*INPUT_FEATURES-1:0]      inputStreams;", 1 )
   write_line( f, "input [OUTPUT_FEATURES*INPUT_FEATURES-1:0] weightStreams;", 1 )
   if not alaghi:
      write_line( f, "input [SELECT_WIDTH-1:0]                 sel;", 1 )
   write_line( f, "output [BATCH_SIZE*OUTPUT_FEATURES-1:0]    outputStreams;", 1 )
   write_line( f, "output                                     outputWriteEn;", 1 )
   write_line( f, "" )
   write_line( f, "genvar i;", 1 )
   write_line( f, "genvar j;", 1 )
   write_line( f, "wire [BATCH_SIZE*OUTPUT_FEATURES-1:0] valids;", 1 )
   write_line( f, "generate", 1 )
   write_line( f, "for( i = 0; i < BATCH_SIZE; i = i + 1) begin : dot_prod_loop", 2 )
   write_line( f, "for( j = 0; j < OUTPUT_FEATURES; j = j + 1) begin", 3 )
   write_line( f, "sc_dot_product DOT_PRODUCT(.clk(clk),", 4 )
   write_line( f, "                .rst(rst),", 4 )
   write_line( f, "                .data(inputStreams[i*INPUT_FEATURES +: INPUT_FEATURES]),", 4 )
   write_line( f, "                .weights(weightStreams[j*INPUT_FEATURES +: INPUT_FEATURES]),", 4 )
   if not alaghi:
      write_line( f, "                .sel(sel),", 4 )
   write_line( f, "                .result(outputStreams[(i*OUTPUT_FEATURES)+j]),", 4 )
   write_line( f, "                .valid(valids[(i*OUTPUT_FEATURES)+j]));", 4 )
   write_line( f, "end", 3 )
   write_line( f, "end", 2 )
   write_line( f, "endgenerate", 1 )
   write_line( f, "" )
   write_line( f, "// later we will incorporate this signal", 1 )
   write_line( f, "assign outputWriteEn = (valids[0] == 1'b1);", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // " + module_name )

# Writes the header comment for the sc_matrix_mult module.
def write_header_mat_mult( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: This module represents matrix multiply in the stochastic domain." )
   write_line( f, "// The inputs to this module are two flattened matrices A and B," )
   write_line( f, "// where A has dimensions MxN and B has dimensions NxO." )
   write_line( f, "// The input matrix B is actually the transpose of B (still flattened)" )
   write_line( f, "// This results in a matrix C with dimensions MxO." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )

# Writes the testbench module for the generated sc_matrix_multiply module.
# Parameters:
# f, file to write to 
# module_name, a string, name of the testbench
# batch, an int, specifies batch size (in a matrix mult MxN * NxO, M is batch size)
# inpt, an int, specifies input feature size (N)
# outpt, an int, specifies output feature size (O)
def write_mm_tb( f, module_name, batch, inpt, outpt, alaghi=False ):
  
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
   write_line( f, MATRIX + " dut(", 1 )
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

# Write the header comment for the matrix multiply module to file, f.
def write_mm_tb_header( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// Description: The module serves as a testbench for the stochastic matrix multiply" )
   write_line( f, "// module." )
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

# Helper function
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

# Helper function
# Converts a number, num, to a binary string of precision n.
def int_to_n_length_binary( num, n ):
   b_str = bin(num)[2:]
   for i in range(0, n - len(b_str)):
      b_str = "0" + b_str

   return b_str

generate( "l", 4,4,4 )
