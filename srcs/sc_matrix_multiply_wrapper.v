
// the precision of the binary numbers we wish our weights and inputs to be
// number of 'cycles' of counting we do during stochastic->digital conversion
//
module sc_matrix_multiply_wrapper(
   parameter BATCH_SIZE = 4, // M
   parameter INPUT_FEATURES = 4, // N
   parameter OUTPUT_FEATURES = 4, // O
   parameter BINARY_PRECISION = 32,
   parameter STOCHASTIC_CYCLES = 1
) (
   clk,
   rst,
   input_matrix,
   weight_matrix,
   enable,
   inputAddr,
   weightAddr,
   output_matrix,
   outputWrEn
);

   input clk;
   input rst;
   input [BATCH_SIZE*INPUT_FEATUES-1:0] input_matrix;
   input [OUTPUT_FEATURES*INPUT_FEATURES-1:0] weight_matrix;
   input enable;
   output inputAddr; // unsure of how to do reads currently
   output weightAddr; // ^^
   output outAddr; // unsure of how to do writes
   output [BATCH_SIZE*OUTPUT_FEATURES-1:0] output_matrix;
   output outputWrEn;  // signal goes high when output_matrix is valid and writable

   // OK...this module will need:
   // M*N SNGs for the input_matrix
   // O*N SNGs for the weight_matrix                    
   // Similarily just as many SD_convertors will be needed
   // We will need 1 matrix multiply module
   // 


endmodule // sc_matrix_multiply_wrapper
