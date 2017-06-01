// the precision of the binary numbers we wish our weights and inputs to be
// number of 'cycles' of counting we do during stochastic->digital conversion
//
module sc_matrix_multiply_ip(
   parameter BATCH_SIZE = 4, // M
   parameter INPUT_FEATURES = 4, // N
   parameter OUTPUT_FEATURES = 4, // O
   parameter BINARY_PRECISION = 8,
   parameter STOCHASTIC_CYCLES = 1
) (
   clk,
   rst,
   input_data,
   weight_data,
   enable,
   inputAddr,
   weightAddr,
   output_data,
   outputWrEn
);

   input clk;
   input rst;
   input enable;
   input [BINARY_PRECISION*INPUT_FEATURES-1:0] input_data;
   input [BINARY_PRECISION*INPUT_FEATURES-1:0] weight_data;
   output inputAddr; // unsure of how to do reads currently
   output weightAddr; // ^^
   output outAddr; // unsure of how to do writes
   output [BINARY_PRECISION*OUTPUT_FEATURES-1:0] output_data;
   output outputWrEn;  // signal goes high when output_matrix is valid and writable

   //TODO We will need a FSM to read and write input data and output

   // Instantiate 2 rng streams
   reg [BINARY_PRECISION-1:0] seed0;
   reg [BINARY_PRECISION-1:0] seed1;
   initial seed0 = BINARY_PRECISION'bxxx...xxx
   initial seed1 = BINARY_PRECISION'bxxx...xxx
   reg [BINARY_PRECISION-1:0] rng0;
   reg [BINARY_PRECISION-1:0] rng1;
   lfsr0 LFSR0( .clk(clk), .rst(rst), .seed(seed0), enable(1), .restart(0), out(rng0) );
   lfsr1 LFSR1( .clk(clk), .rst(rst), .seed(seed1), enable(1), .restart(0), out(rng1) );
   
   // Instantiate 2N stochastic number generators for the current
   // input vector and weight vector.
   wire [BATCH_SIZE*INPUT_FEATURES-1:0] stoch_inputs;
   wire [BATCH_SIZE*INPUT_FEATURES-1:0] stoch_weights;
   genvar n;
   generate
      for( n = 0; n < INPUT_FEATURES; n = n + 1 ) begin
         sng INPUT_SNG( 
            .clk(clk), 
            .rst(rst), 
            .in(input_data[(n*BINARY_PRECISION) +: BINARY_PRECISION]), 
            .out(stoch_inputs[n])
         );
         sng WEIGHT_SNG(
            .clk(clk),
            .rst(rst),
            .in(weight_data[(n*BINARY_PRECISION) +: BINARY_PRECISION]),
            .out(stoch_weights[n])
         );
      end
   endgenerate

   // if alaghi:
   //    no select stream
   // else:
    
   // Generate the select streams for addition operations within the matrix
   // multiply module. We will need INPUT_FEATURES number of select streams.
   parameter log_input_features = clogb2(INPUT_FEATURES)
   wire [log_input_features-1:0] selects;
   counter COUNTER( .clk(clk), .rst(rst), .enable(1), .restart(0), .out(selects) );

   // The core of the computation, the dot_product module
   wire result;
   reg valid;
   sc_dot_product SC_DOT_PRODUCT(
      .clk(clk),
      .rst(rst),
      .data(stoch_inputs),
      .weights(stoch_weights),
      .sel(selects),
      .result(result),
      .valid(valid)
   );

   // We want a counter to determine when to stop counting the stochastic
   // output streams. We will count for 2^BINARY_PRECISION posedges before
   // ending and finally outputting the binary number.
   reg [BINARY_PRECISION-1:0] conv_counter; 
   reg last;
   initial conv_counter = 0;
   initial last = 0;
   // when the MSB of last goes high, we stop counting, reset the counter, and
   // set outputWrEn to high.
   //
   // Also this is incorrect, we only want to begin our counter when the
   // output of the matrix multiply is valid.
   always @(posedge clk) begin
      if(rst == 1) begin
         conv_counter <= 0;
         last <= 0;
      end else if(conv_counter == BINARY_PRECISION'b111...1) begin
         conv_counter <= 0;
         last <= 1;
      end else begin
         conv_counter <= conv_counter + 1;
         last <= 0;
      end
   end

   wire [BINARY_PRECISION-1:0] binary_out;
   sd_converter #(BINARY_PRECISION) SD_CONV( 
      .clk(clk),
      .rst(rst),
      .in(result),
      .last(last),
      .out(binary_out)
   );

endmodule // sc_matrix_multiply_wrapper
