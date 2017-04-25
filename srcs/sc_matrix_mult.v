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

// right now im thinking we could read in the entirity of both matrices and then
// write the entirity of one matrix...because a stochastic matrix is just N*M bits.
//
// Hold up...do we even need to write an output matrix to memory? Probably, but its weird to
// think of it like this, because one needs a stream that represents the matrix. (would have to write a whole matrix every cycle).

module sc_matrix_mult #(
   parameter BATCH_SIZE = 4 // M
   parameter INPUT_FEATURES = 4 // N
   parameter OUTPUT_FEATURES = 4 // O
) (
   input clk,
   input [BATCH_SIZE*INPUT_FEATURES-1:0] inputData,
   input [OUTPUT_FEATURES*INPUT_FEATURES-1:0] weightData,
   output [BATCH_SIZE*OUTPUT_FEATURES-1:0] outputData
);

endmodule // sc_matrix_mult
