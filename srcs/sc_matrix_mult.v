//////////////////////////////////////////////////////////////////////////////////
// Author: Gyorgy Wyatt Muntean 2017
// Create Date: 04/24/2017 6:37pm
//
// Description: The module represents matrix multiply in the stochastic domain.
// The inputs to this module are two flattened matrices A and B,
// where A has dimensions MxN and B has dimensions NxO. 
// The input matrix B however should be the flattened form of the transpose of B.
// This results in a matrix C with dimensions MxO.
//
// For more information on stochastic computing: 
// https://en.wikipedia.org/wiki/Stochastic_computing
//
//////////////////////////////////////////////////////////////////////////////////

module sc_matrix_mult #(
   parameter BATCH_SIZE = 4, // M
   parameter INPUT_FEATURES = 4, // N
   parameter OUTPUT_FEATURES = 4 // O
) (
   input clk,
   input rst,
   input [BATCH_SIZE*INPUT_FEATURES-1:0] inputStreams,
   input [OUTPUT_FEATURES*INPUT_FEATURES-1:0] weightStreams,
   input [INPUT_FEATURES-2:0] sel,
   output [BATCH_SIZE*OUTPUT_FEATURES-1:0] outputStreams,
   output valid
);

   // Instantiate M*O dot product modules, so all computation is done in
   // parallel. All modules will begin to output after some latency, then
   // valid will be set to high and outputStreams will hold the stochastic
   // bitstreams of the output features.
   genvar i, j;
   generate
      for( i = 0; i < BATCH_SIZE; i = i + 1) begin 
         for( j = 0; j < OUTPUT_FEATURES; j = j + 1) begin : dot_prod_loop
            sc_dot_product #(INPUT_FEATURES) (.clk(clk), 
                                              .rst(rst), 
                                              .data(inputStreams[i*INPUT_FEATURES +: INPUT_FEATURES]),
                                              .weights(weightStreams[j*INPUT_FEATURES +: INPUT_FEATURES]),
                                              .sel(sel),
                                              .result(outputStreams[(i*OUTPUT_FEATURES)+j]));
         end
      end
   endgenerate
  
   // later we will incorporate this signal 
   assign valid = 1;

endmodule // sc_matrix_mult
