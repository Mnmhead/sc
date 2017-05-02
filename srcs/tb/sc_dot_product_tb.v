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
   parameter LENGTH = 4;
   parameter SELECT_WIDTH = 2;

   reg                    clk;
   reg                    rst;
   reg [LENGTH-1:0]       data;
   reg [LENGTH-1:0]       weights;  
   reg [SELECT_WIDTH-1:0] sel;
   wire                   result; 

   // Clock Generation
   parameter CLOCK_PERIOD=10;
   initial Clock=1;
   always begin
      #(CLOCK_PERIOD/2);
      Clock = ~Clock;
   end

   sc_dot_product dut( .clk(clk), .rst(rst), .data(data), .weights(weights), .sel(sel), .result(result) ); 

   integer errors;
   initial errors = 0;   
   initial begin
      // initialize inputs
      rst = 1;
      data = 0;
      weights = 0;
      sel = 0; 

      // start sim
      rst = 0;

      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);

      // error summary
      if( errors > 0 ) begin
          $display("Validataion failure: %d error(s).", errors);
      end else begin
            $display("Validation successful.");
      end

      $stop;
   end
endmodule // sc_dot_product_tb
