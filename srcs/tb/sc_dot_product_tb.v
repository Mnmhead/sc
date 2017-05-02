//////////////////////////////////////////////////////////////////////////////////
// Create Date: 2017-05-01 19:41:46 GMT
//
// Description: The module serves as a testbench for the stochastic dot product module.
// For more information on stochastic computing: https://en.wikipedia.org/wiki/Stochastic_computing
//
// Requirements:
// The input 'sel' must be the concatenation of clog2(LENGTH) number of un-correlated 
// stochastic streams (each with value=0.5).
//////////////////////////////////////////////////////////////////////////////////
`timescale 1ns / 10ps

module sc_dot_product_tb();
   parameter LENGTH =        4;
   parameter SELECT_WIDTH =  2;
   parameter DATA_VECTOR =   "data_vectors.mif";
   parameter WEIGHT_VECTOR = "weight_vectors.mif";
   parameter SELECT_STREAM = "select_streams.mif";
   parameter DP_RESULT =     "dp_results.mif";
   parameter TEST_SIZE =     100;

   // module inputs and outputs
   reg                     clk;
   reg                     rst;
   wire [LENGTH-1:0]       data;
   wire [LENGTH-1:0]       weights;  
   wire [SELECT_WIDTH-1:0] sel;
   wire                    result; 
   wire                    valid;

   // read input data and expected output data
   reg [LENGTH-1:0] test_data [TEST_SIZE-1:0];  // i think this only needs to be clogb2 of TEST_SIZE
   reg [LENGTH-1:0] test_weights [TEST_SIZE-1:0];
   reg [SELECT_WIDTH-1:0] test_sel [TEST_SIZE-1:0]; 
   reg expexted_result [TEST_SIZE-1:0];
   initial begin
      $readmemb(DATA_VECTOR, test_data, 0, TEST_SIZE-1);
      $readmemb(WEIGHT_VECTOR, test_weights, 0, TEST_SIZE-1);
      $readmemb(SELECT_STREAM, test_sel, 0, TEST_SIZE-1);
      $readmemb(DP_RESULT, expected_result, 0, TEST_SIZE-1);
   end

   // Test input assignment logic
   reg [6:0] test_index; // clogb2(TEST_SIZE)
   initial test_index = 0;
   always @(posedge clk) begin
      if( rst == 1'b1 ) begin
         test_index <= 0;
      end else begin
         test_index <= test_index + 1;
      end
   end
   assign data = test_data[test_index];
   assign weights = test_weights[test_index];
   assign sel = test_sel[test_index];

   // Output checking and error handling
   integer result_index;
   integer errors;
   initial result_index = 0;
   initial errors = 0;
   always @(posedge clk) begin
      if( rst ) begin
         result_index <= 0;
      end else if( valid == 1'b1 ) begin
         if( result != expected_result[result_index] ) begin
            $display("Error. Expected result %d foes not match actual %d.", 
                     expected_result[result_index], result );
            errors = errors + 1;
         end

         result_index = result_index + 1;
      end
   end

   // Clock Generation
   parameter CLOCK_PERIOD=10;
   initial Clock=1;
   always begin
      #(CLOCK_PERIOD/2);
      Clock = ~Clock;
   end

   // instantiate module
   sc_dot_product dut( 
      .clk(clk), 
      .rst(rst), 
      .data(data), 
      .weights(weights), 
      .sel(sel), 
      .result(result), 
      .valid(valid) 
   ); 

   initial begin
      // initialize inputs
      rst = 1;
      data = 0;
      weights = 0;
      sel = 0; 
      #(8*CLOCK_PERIOD);

      // start sim
      rst = 0;
      #(TEST_SIZE*CLOCK_PERIOD + 100) // add 100 extra cycles for initial ouput delay

      // error summary
      $display("Simulation complete.");
      if( errors > 0 ) begin
          $display("Validataion failure: %d error(s).", errors);
      end else begin
            $display("Validation successful.");
      end

      $stop;
   end
endmodule // sc_dot_product_tb
