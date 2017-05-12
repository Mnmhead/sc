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
   input [BINARY_PRECISION*BATCH_SIZE*INPUT_FEATURES-1:0] input_matrix;
   input [BINARY_PRECISION*OUTPUT_FEATURES*INPUT_FEATURES-1:0] weight_matrix;
   input enable;
   output inputAddr; // unsure of how to do reads currently
   output weightAddr; // ^^
   output outAddr; // unsure of how to do writes
   output [BINARY_PRECISION*BATCH_SIZE*OUTPUT_FEATURES-1:0] output_matrix;
   output outputWrEn;  // signal goes high when output_matrix is valid and writable

   //TODO We will need a FSM to read and write input data and output
   
   // Instantiate M*N stochastic number generators for the input_matrix
   wire [BATCH_SIZE*INPUT_FEATURES-1:0] stoch_inputs;
   genvar m;
   genvar n;
   generate
      for( m = 0; m < BATCH_SIZE; m = m + 1 ) begin : input_sng_loop
         for( n = 0; n < INPUT_FEATURES; n = n + 1 ) begin
            sng #(BINARY_PRECISION) INPUT_SNG( 
         .clk(clk), 
         .rst(rst), 
         .in(input_matrix[((m*INPUT_FEATURES*BINARY_PRECISION) + (n*BINARY_PRECISION)) +: BINARY_PRECISION]), 
         .out(stoch_inputs[(m*INPUT_FEATURES) + n])
            );
         end
      end
   endgenerate
   
   // Instantiate M*N stochastic number generators for the input_matrix
   wire [BATCH_SIZE*INPUT_FEATURES-1:0] stoch_weights;
   genvar o;
   genvar n;
   generate
      for( o = 0; o < OUTPUT_FEATURES; o = o + 1 ) begin : weight_sng_loop
         for( n = 0; n < INPUT_FEATURES; n = n + 1 ) begin
            sng #(BINARY_PRECISION) WEIGHT_SNG( 
         .clk(clk), 
         .rst(rst), 
         .in(weight_matrix[((o*INPUT_FEATURES*BINARY_PRECISION) + (n*BINARY_PRECISION)) +: BINARY_PRECISION]), 
         .out(stoch_weights[(o*INPUT_FEATURES) + n])
            );
         end
      end
   endgenerate

   // Generate the select streams for addition operaitons within the matrix
   // multiply module. We will need INPUT_FEATURES number of select streams.
   // lfsr or counter or some shit.
   wire [INPUT_FEATURES-1:0] selects;

   // TODO code for select streams here


   // The core of the computation, the matrix multiply module
   wire [BATCH_SIZE*OUTPUT_FEATURES-1:0] stoch_output;
   wire sc_mm_valid;
   sc_matrix_mult MATRIX_MULT(
      .clk(clk), 
      .rst(rst), 
      .inputStreams(stoch_inputs),
      .weightStreams(stoch_weights),
      .sel(selects),
      .outputStreams(stoch_output),
      .outputWriteEn(sc_mm_valid)
   );

   // We want a counter to determine when to stop counting the stochastic
   // output streams. We will count for 2^BINARY_PRECISION posedges before
   // ending and finally outputting the binary number.
   reg [BINARY_PRECISION:0] last; 
   // when the MSB of last goes high, we stop counting, reset the counter, and
   // set outputWrEn to high.
   //
   // Also this is incorrect, we only want to begin our counter when the
   // output of the matrix multiply is valid.
   always @ (posedge clk) begin
      if(rst == 1) begin
         last <= 0;
      end else if (last[BINARY_PRECISION] == 1) begin
         last <= 0;
      end else begin
         last <= last + 1;
      end
   end

   // I guess this works??
   assign outputWrEn = (last[BINARY_PRCISION] == 1)

   // When the stoch_output becomes valid we need to convert it out to the
   // digital domain. Thus we stamp out M*O stochastic to digital convertors.
   generate
      for( m = 0; i < BATCH_SIZE; m = m + 1 ) begin : output_sd_loop
         for( o = 0; o < OUTPUT_FEATURES; o = o + 1 ) begin
            sd_converter #(BINARY_PRECISION) SD_CONV( 
         .clk(clk),
         .rst(rst),
         .in(stoch_output[(m*OUTPUT_FEATURES) + o]),
         .last(),
         .out(output_matrix[(m*OUTPUT_FEATURES*BINARY_PRECISION) + (o*BINARY_PRECISION) +: BINARY_PRECISION])
            );
         end
      end
   endgenerate
endmodule // sc_matrix_multiply_wrapper
