# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains functions to generate the core modules for
# stochastic matrix multiply. 

from common import *
import counter_gen
import lfsr_gen
import numpy as np
import os
import sc_dot_product_gen
import sd_converter_gen
import sng_gen

# Generates simulation modules for the following stochastic
# circuits: dot_product, matrix_multiply
# args, the parser arguments from generate.py
def generate( dest, dimensions, precision ):
   # generate width 8 lfsr
   lfsr_gen.generate( dest, precision ) 

   # generate modular counter which counts upto 4 for select streams
   counter_gen.generate( dest, dimensions )

   # generate an sd_convertor which converts to an 8 bit binary number
   sd_converter_gen.generate( dest, precision )

   # generate sng which takes 8bit binary numbers
   sng_gen.generate( dest, precision )

   # generate the dot product module!
   sc_dot_product_gen.generate( dest, dimensions )

   with open( os.path.join( dest, DOT_PROD_SIM + ".v" ), 'w' ) as f:
      write_header_dp_sim( f )
      write_dot_product_simulation( f, DOT_PROD_SIM, dimensions, precision )

def write_dot_product_simulation( f, module_name, dimensions, precision, rep = "uni", alaghi = False ):
   write_line( f, "module sc_dot_product_sim();" )
   write_line( f, "parameter DIMENSION = " + str(dimensions) + ";", 1 )
   write_line( f, "parameter WIDTH     = " + str(precision) + ";", 1 )
   write_line( f, "" )
   write_line( f, "reg                       clk;", 1 )
   write_line( f, "reg                       rst;", 1 )
   write_line( f, "reg [WIDTH*DIMENSION-1:0] datas;", 1 )
   write_line( f, "reg [WIDTH*DIMENSION-1:0] weights;", 1 )
   write_line( f, "" )
   write_line( f, "// Clock Generation", 1 )
   write_line( f, "parameter CLOCK_PERIOD=10;", 1 )
   write_line( f, "initial clk=1;", 1 )
   write_line( f, "always begin", 1 )
   write_line( f, "#(CLOCK_PERIOD/2);", 2 )
   write_line( f, "clk = ~clk;", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )

   # generate random data and weights, compute actual binary result
   A = np.random.randint( pow(2, precision), size = dimensions )
   B = np.random.randint( pow(2, precision), size = dimensions )
   A_str = vector_to_verilog_bit_string( A, precision )
   B_str = vector_to_verilog_bit_string( B, precision )

   expected_dp = 0
   for d in range(dimensions):
      expected_dp += A[d] * B[d] 

   write_line( f, "initial datas = " + A_str + ";", 1 )
   write_line( f, "initial weights = " + B_str + ";", 1 )
   write_line( f, "integer expected_result;", 1 )
   write_line( f, "initial expected_result = " + str(expected_dp) + ";", 1 )

   # generate random seeds for lfsr
   # generate 2 unique numbers between 0-2^(precision-1)
   seed0 = np.random.randint( pow(2, precision) )
   seed1 = np.random.randint( pow(2, precision) )
   # assert that the seeds are different
   while seed1 == seed0:
      seed1 = np.random.randint( pow(2, precision) )

   write_line( f, "// Instantiate noise sources. Only two are required, only multipliers", 1 )
   write_line( f, "// required uncorrelated streams.", 1 )
   write_line( f, "reg [WIDTH-1:0] seed0;", 1 )
   write_line( f, "reg [WIDTH-1:0] seed1;", 1 )
   write_line( f, "initial seed0 = " + str(seed0) + ";", 1 )
   write_line( f, "initial seed1 = " + str(seed1) + ";", 1 )
   write_line( f, "wire [WIDTH-1:0] rng0;", 1 )
   write_line( f, "wire [WIDTH-1:0] rng1;", 1 )
   write_line( f, "lfsr LFSR1(.clk(clk), .rst(rst), .seed(seed0), .enable(1'b1), .restart(1'b0), .out(rng0));", 1 )
   write_line( f, "lfsr LFSR2(.clk(clk), .rst(rst), .seed(seed1), .enable(1'b1), .restart(1'b0), .out(rng1));", 1 )
   write_line( f, "" )
   write_line( f, "// Instantiate the SNGs to produce stochastic bitstreams for all", 1 )
   write_line( f, "// data and weights.", 1 )
   write_line( f, "wire [DIMENSION-1:0] s_datas;", 1 )
   write_line( f, "wire [DIMENSION-1:0] s_weights;", 1 )
   write_line( f, "genvar d;", 1 )
   write_line( f, "generate", 1 )
   write_line( f, "for(d = 0; d < DIMENSION; d = d + 1) begin : sng_loop", 2 )
   write_line( f, "sng DATA_SNG(", 3 )
   write_line( f, ".clk(clk),", 4 )
   write_line( f, ".rst(rst),", 4 )
   write_line( f, ".in(datas[d*WIDTH +: WIDTH]),", 4 )
   write_line( f, ".rng(rng0),", 4 )
   write_line( f, ".out(s_datas[d])", 4 )
   write_line( f, ");", 3 )
   write_line( f, "sng WEIGHT_SNG(", 3 )
   write_line( f, ".clk(clk),", 4 )
   write_line( f, ".rst(rst),", 4 )
   write_line( f, ".in(weights[d*WIDTH +: WIDTH]),", 4 )
   write_line( f, ".rng(rng1),", 4 )
   write_line( f, ".out(s_weights[d])", 4 )
   write_line( f, ");", 3 )
   write_line( f, "end", 2 )
   write_line( f, "endgenerate", 1 )
   write_line( f, "" )
   if not alaghi:
      write_line( f, "// Generate a select stream for the adder.", 1 )
      write_line( f, "wire [" + str(clogb2( dimensions )) + "-1:0] sel;", 1 )
      write_line( f, "counter COUNTER(.clk(clk), .rst(rst), .enable(1'b1), .restart(1'b0), .out(sel));", 1 )
      write_line( f, "" )
   write_line( f, "// Instantiate the dot product module", 1 )
   write_line( f, "wire result;", 1 )
   write_line( f, "wire valid;", 1 )
   write_line( f, "sc_dot_product DOT_PRODUCT(", 1 )
   write_line( f, ".clk(clk),", 2 )
   write_line( f, ".rst(rst),", 2 )
   write_line( f, ".data(s_datas),", 2 )
   write_line( f, ".weights(s_weights),", 2 )
   if not alaghi:
      write_line( f, ".sel(sel),", 2 )
   write_line( f, ".result(result),", 2 )
   write_line( f, ".valid(valid)", 2 )
   write_line( f, ");", 1 )
   write_line( f, "" )
   write_line( f, "// Pipe the result into a sd convertor as soon as valid goes high", 1 )
   write_line( f, "wire [WIDTH-1:0] non_scaled_binary_result;", 1 )
   write_line( f, "reg [WIDTH-1:0] last_counter;", 1 )
   write_line( f, "reg last;", 1 )
   write_line( f, "reg in_stream;", 1 )
   write_line( f, "initial last_counter = 0;", 1 )
   write_line( f, "initial last = 0;", 1 )
   write_line( f, "always @(posedge clk) begin", 1 )
   write_line( f, "if(rst == 1) begin", 2 )
   write_line( f, "last_counter <= 0;", 3 )
   write_line( f, "last <= 0;", 3 )
   write_line( f, "in_stream <= 0;", 3 )
   write_line( f, "end else if( valid == 1'b1 ) begin", 2 )
   last = pow(2, precision) - 1
   write_line( f, "if( last_counter == " + str(last) + " ) begin", 3 )
   write_line( f, "last <= 1;", 4 )
   write_line( f, "last_counter <= 0;", 4 )
   write_line( f, "end else begin", 3 )
   write_line( f, "last <= 0;", 4 )
   write_line( f, "last_counter <= last_counter + 1;", 4 )
   write_line( f, "end", 3 )
   write_line( f, "" )
   write_line( f, "in_stream <= result;", 3 )
   write_line( f, "end else begin", 2 )
   write_line( f, "last_counter <= 0;", 3 )
   write_line( f, "last <= 0;", 3 )
   write_line( f, "in_stream <= 0;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "sd_converter SD_CONVERTER(", 1 )
   write_line( f, ".clk(clk),", 2 )
   write_line( f, ".rst(rst),", 2 )
   write_line( f, ".in(in_stream),", 2 )
   write_line( f, ".last(last),", 2 )
   write_line( f, ".out(non_scaled_binary_result)", 2 )
   write_line( f, ");", 1 )
   write_line( f, "" )
   res_width = 2 * precision + clogb2(dimensions)
   write_line( f, "wire [" + str(res_width) + "-1:0] dot_product;", 1 )
   write_line( f, "assign dot_product = non_scaled_binary_result * " \
                  + str(dimensions) + " * " + str(pow( 2, precision )) + ";", 1 )
   write_line( f, "" )
   write_line( f, "wire done;", 1 )
   write_line( f, "assign done = (last == 1'b1);", 1 )
   write_line( f, "always @(*) begin", 1 )
   write_line( f, "if(done) begin", 2 )
   write_line( f, "$display(\"expected result = %d\\n actual result = %d\\n\", expected_result, dot_product );", 3 )
   write_line( f, "$display(\"DONE!\\n\" );", 3 )
   write_line( f, "$stop;", 3 )
   write_line( f, "end", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "initial begin", 1 )
   write_line( f, "rst = 1;", 2 )
   write_line( f, "#(4*CLOCK_PERIOD);", 2 )
   write_line( f, "rst = 0;", 2 )
   write_line( f, "end", 1 )
   write_line( f, "" )
   write_line( f, "endmodule // sc_dot_product_sim" )

# writes header comment for dp sim module
def write_header_dp_sim( f ):
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "// Create Date: " + get_time() )
   write_line( f, "//" )
   write_line( f, "// This module serves as a simulation test bench for the stochastic dot product" )
   write_line( f, "// module. At the end of simulation the expected binary result and actual" )
   write_line( f, "// stochastic result are displayed in console." )
   write_line( f, "//////////////////////////////////////////////////////////////////////////////////" )
   write_line( f, "" )


def vector_to_verilog_bit_string( v, precision ):
   dim = len(v)
   length = dim * precision

   s = str(length) + "\'b"
  
   # form strings for each element in vector 'v' 
   for el in v:
      el_str = bin(el)[2:]
      # append 0's to front until string is length 'precision'
      for i in range(0, precision - len(el_str)):
         el_str = "0" + el_str
      s += el_str
      
   return s

generate( "test", 4, 8 )
