//////////////////////////////////////////////////////////////////////////////////
// Create Date: 2017-05-01 19:41:46 GMT
//
// Description: The module serves as a testbench for the stochastic matrix multiply 
// module.
//////////////////////////////////////////////////////////////////////////////////

module sc_matrix_multiply_tb();
   parameter BATCH_SIZE =      4; // M
   parameter INPUT_FEATURES =  4; // N
   parameter OUTPUT_FEATURES = 4; // O
   parameter SELECT_WIDTH =    2;
   parameter INPUT_MATRICES =  "input_matrices.mif";
   parameter WEIGHT_MATRICES = "weight_matrices.mif";
   parameter SELECT_STREAM =   "mm_select_streams.mif";
   parameter MM_RESULT =       "mm_results.mif";
   parameter TEST_SIZE =       250;

   // module inputs and outputs
   reg clk;
   reg rst;
   reg [BATCH_SIZE*INPUT_FEATURES-1:0] inputStreams
   reg [OUTPUT_FEATURES*INPUT_FEATURES-1:0] weightStreams;
   reg [SELECT_WIDTH-1:0]                 sel;
   wire [BATCH_SIZE*OUTPUT_FEATURES-1:0]    outputStreams;
   wire                                     outputWriteEn; 

   // read input data and expected output data
   reg [BATCH_SIZE*INPUT_FEATURES-1:0] test_input [TEST_SIZE-1:0];
   reg [OUTPUT_FEATURES*INPUT_FEATURES-1:0] test_weight [TEST_SIZE-1:0];
   reg [SELECT_WIDTH-1:0]                 test_sel [TEST_SIZE-1:0];
   reg [BATCH_SIZE*OUTPUT_FEATURES-1:0] expected_results [TEST_SIZE-1:0];
   initial begin
      $readmemb(INPUT_MATRICIES, test_input, 0, TEST_SIZE-1);
      $readmemb(WEIGHT_MATRICIES, test_weight, 0, TEST_SIZE-1);
      $readmemb(SELECT_STREAM, test_sel, 0, TEST_SIZE-1);
      $readmemb(MM_RESULT, test_expected_results, 0, TEST_SIZE-1);
   end

   // Test input assignment logic
   reg [7:0] test_index; 
   initial test_index = 0;
   always @(posedge clk) begin
      if( rst == 1'b1 ) begin
         test_index <= 0;
      end else begin
         test_index <= test_index + 1;
      end
   end
   assign inputStreams = test_input[test_index];
   assign weightStreams = test_input[test_index];
   assign sel = test_sel[test_index];

   // output checking and error handling
   integer result_index;
   integer errors;
   initial result_index = 0;
   initial errors = 0;
    always @(posedge clk) begin
      if( rst ) begin
         result_index <= 0;
      end else if( outputWriteEn == 1'b1 ) begin
         if( outputStreams != expected_results[result_index] ) begin
            $display("Error. Expected result %B does not match actual %B. On result index: %d",
                     expected_results[result_index], outputStreams, result_index);
            errors = errors + 1;
         end

         result_index = result_index + 1;
      end
   end

   // Clock Generation
   parameter CLOCK_PERIOD=10;
   initial clk=1;
   always begin
      #(CLOCK_PERIOD/2);
      clk = ~clk;
   end

   // instantiate module
   sc_matrix_multiply dut(
      clk,
      rst,
      inputStreams,
      weightStreams,
      sel,
      outputStreams,
      outputWriteEn
   );

   initial begin
      rst = 1;
      #(8*CLOCK_PERIOD);

      // start sim
      rst = 0;
      #(TEST_SIZE*CLOCK_PERIOD + 100)  // give 100 clock cycles for initial output delay

      // error summary
      $display("Simulation complete.");
      if( errors > 0 ) begin
          $display("Validataion failure: %d error(s).", errors);
      end else begin
            $display("Validation successful.");
      end

      $stop;
   end
endmodule // sc_matrix_multiply_tb
