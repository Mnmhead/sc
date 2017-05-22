//////////////////////////////////////////////////////////////////////////////////
// Create Date: 2017-05-01 19:41:46 GMT
//
// Description: This module serves as a testbench for the sc_nadder module.
// For more information on stochastic computing: https://en.wikipedia.org/wiki/Stochastic_computing
//////////////////////////////////////////////////////////////////////////////////
`timescale 1ns / 10ps

module alaghi_nadder_tb();
   parameter INPUT_STREAMS = 31;
   parameter DELAY = X;
   parameter INPUTS =        "adder_inputs.mif";
   parameter ADDER_RESULT =  "adder_results.mif";
   parameter TEST_SIZE =     100

   // modules inputs and outputs
   reg                     clk;
   reg                     rst;
   reg [INPUT_STREAMS-1:0] inpts;
   wire                    out;

   // read input data and expected results data
   reg [INPUT_STREAMS-1:0] test_inputs [TEST_LENGTH-1:0];
   reg expected_results [TEST_LENGTH-1:0];
   initial begin
      $readmemb(INPUTS, test_inputs, 0, TEST_LENGTH-1);
      $readmemb(ADDER_RESULT, expected_results, 0, TEST_LENGTH-1);
   end

   // Test input data assignment logic
   reg [TEST_LENGTH-1:0] test_index;
   initial test_index = 0;
   always @(posedge clk) begin
      if( rst == 1'b1 ) begin
         test_index <= 0;
      end else begin
         test_index <= test_index + 1;
      end
   end
   assign inpts = test_inputs;

   // Output checking and error handling
   reg valid;
   reg [TEST_LENGTH-1:0] valid_delay;
   always @(posedge clk) begin
      if( rst ) begin
         valid <= 0;
      end else begin
         if( valid_delay == DELAY ) begin
            valid <= 1; 
         end else begin
            valid_delay <= valid_delay + 1 
         end
      end
   end
   integer result_index;
   integer errors;
   initial result_index = 0;
   initial errors = 0;
   always @(posedge clk) begin
      if( rst ) begin
         result_index <= 0;
      end else if( valid == 1'b1 ) begin
         if( result != expected_result[result_index] ) begin
            $display("Error. Expected result %d does not match actual %d. On result index: %d",
                     expected_result[result_index], out, result_index);
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
   alaghi_nadder dut(.clk(clk), .rst(rst), .inpts(inpts), .out(out));

   initial begin
      // initialize inputs
      rst = 1;
      #(8*CLOCK_PERIOD);

      // start sim
      rst = 0;
      #(TEST_LENGTH*CLOCK_PERIOD + 2*DELAY);

      // error summary
      $display("Simulation complete.");
      if( errors > 0 ) begin
          $display("Validataion failure: %d error(s).", errors);
      end else begin
            $display("Validation successful.");
      end

      $stop;
   end
endmodule // alaghi_nadder_tb
