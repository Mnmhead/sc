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
   output inputAddr;
   output weightAddr;
   output outAddr;
   output [BINARY_PRECISION*OUTPUT_FEATURES-1:0] output_data;
   output outputWrEn;  // signal goes high when output_matrix is valid and writable

   // Instantiate 2 rng streams
   reg [BINARY_PRECISION-1:0] seed0;
   reg [BINARY_PRECISION-1:0] seed1;
   initial seed0 = BINARY_PRECISION'bxxx...xxx;
   initial seed1 = BINARY_PRECISION'bxxx...xxx;
   reg [BINARY_PRECISION-1:0] rng0;
   reg [BINARY_PRECISION-1:0] rng1;
   lfsr0 LFSR0( .clk(clk), .rst(rst), .seed(seed0), enable(1), .restart(0), out(rng0) );
   lfsr1 LFSR1( .clk(clk), .rst(rst), .seed(seed1), enable(1), .restart(0), out(rng1) );
   
   // Instantiate 2N stochastic number generators for the current
   // input vector and weight vector.
   reg [BINARY_PRECISION*INPUT_FEATURES-1:0] input_buffer;
   reg [BINARY_PRECISION*INPUT_FEATURES-1:0] weight_buffer;
   wire [INPUT_FEATURES-1:0] stoch_inputs;
   wire [INPUT_FEATURES-1:0] stoch_weights;
   genvar n;
   generate
      for( n = 0; n < INPUT_FEATURES; n = n + 1 ) begin
         sng INPUT_SNG( 
            .clk(clk), 
            .rst(rst), 
            .in(input_buffer[(n*BINARY_PRECISION) +: BINARY_PRECISION]), 
            .out(stoch_inputs[n])
         );
         sng WEIGHT_SNG(
            .clk(clk),
            .rst(rst),
            .in(weight_buffer[(n*BINARY_PRECISION) +: BINARY_PRECISION]),
            .out(stoch_weights[n])
         );
      end
   endgenerate

   // if alaghi:
   //    no select stream needed
   // else:
    
   // Generate the select streams for addition operations within the matrix
   // multiply module. (Modular counter from 0 to input_features-1)
   parameter log_input_features = clogb2(INPUT_FEATURES);
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
   // finally outputting the binary number.
   reg [BINARY_PRECISION-1:0] conv_counter; 
   reg last;
   initial conv_counter = 0;
   initial last = 0;
   // when all of last goes high, we stop counting, reset the counter, 
   // direct the binary_output to a register, and set outEn to high.
   wire [BINARY_PRECISION-1:0] binary_out;
   reg [BINARY_PRECISION-1:0] binary_out_reg;
   reg outEn_reg;
   always @(posedge clk) begin
      if(rst == 1 || valid == 0) begin
         conv_counter <= 0;
         last <= 0;
         outEn_reg <= 0;
      end else if(conv_counter == BINARY_PRECISION'b111...1) begin
         conv_counter <= 0;
         last <= 1;
         binary_out_reg <= binary_out;
         outErn_reg <= 1;
      end else begin
         conv_counter <= conv_counter + 1;
         last <= 0;
         outEn_reg <= 0;
      end
   end

   sd_converter #(BINARY_PRECISION) SD_CONV( 
      .clk(clk),
      .rst(rst),
      .in(result),
      .last(last),
      .out(binary_out)
   );

   assign output_data = binary_out_reg;
   assign outputWrEn = outEn_reg;

   //TODO We will need a FSM to read and write input data and output
   parameter IDLE = 3'b000;
   parameter INIT = 3'b001;
   parameter READ = 3'b010;
   parameter COMPUTE = 3'b011;
   parameter FINISH = 3'b100;
   reg [2:0] sm;
   initial sm = IDLE;

   reg [31:0] inAddr_reg;
   reg [31:0] wAddr_reg;
   reg [31:0] outAddr_reg;
   reg [clogb2(batch)-1:0] batchIdx;
   reg [clogb2(output_features)-1:0] outIdx;
   initial batchIdx = 0;
   initial outIdx = 0;
   //parameter initInAddr = 0x2000000;
   //parameter initWAddr = 0x30000000;
   //parameter initOutAddr = 0x40000000;
   //parameter readSize = BINARY_PRECISION * INPUT_FEATURES; // (in bits)
   //parameter write_size = OUTPUT_PRECISION * OUTPUT_FEATURES; // (in bits)
   //initial inAddr_reg = initInAddr;
   //initial wAddr_reg = initWAddr;
   //initial outAddr_reg = initOutAddr;
   assign inputAddr = inAddr_reg;
   assign weightAddr = wAddr_reg;
   assign outAddr = outAddr_reg;

   reg [BINARY_PRECISION*INPUT_FEATURES-1:0] next_inputs;
   reg [BINARY_PRECISION*INPUT_FEATURES-1:0] next_weights;


   // NOTE: a critical assumption made by this code is that
   // a read only takes 1 clock cycle...I hope this is an ok assumption
   // to make.
   always @(posedge clk) begin
   
      case(sm)
         IDLE:
            begin
               if(rst == 1'b1) begin
                  sm <= IDLE;
               end else begin
                  sm <= INIT;
               end
            end

         INIT:
            begin
               // read first row
               input_buffer <= input_data;
               weight_buffer <= weight_data;
               // increment Reading addresses and transition to READ
               //inAddr_reg <= inAddr_reg + readSize;
               wAddr_reg <= wAddr_reg + readSize;
               sm <= READ;
            end

         READ:
            begin
               // read the next row and save it in registers
               next_inputs <= input_data;
               next_weights <= weight_data;
               sm <= COMPUTE;
            end

         COMPUTE:
            begin
               // this can sort of be like an idle state, but computation is happening
               // and we wait for last to go high
               // when last goes high, transition to READ, but after setting the new SNG input
               // but if there is no row to read... transition to FINISH...
               if(last == 1'b1) begin
                  // pipe the next inputs into the SNGs
                  input_buffer <= next_inputs;
                  weight_buffer <= next_weights;
                  // increment reading and writing addresses ( we just finished a row)
                  inAddr_reg <= inAddr_reg + readSize;
                  wAddr_reg <= wAddr_reg + readSize; 
                  outAddr_reg <= outAddr + writeSize;
                  // transition back to the READ state (in order to read next inputs)
                  if 
                  sm <= READ;
               end else begin
                  sm <= 
               end

            end

         FINISH:
            begin
              // once the final last == final_count goes high clear all intermediate registers
              // and shit.
            end

         default:
            sm <= IDLE;
      endcase
   end

endmodule // sc_matrix_multiply_ip
