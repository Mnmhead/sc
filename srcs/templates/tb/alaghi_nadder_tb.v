//////////////////////////////////////////////////////////////////////////////////
// Create Date: 2017-05-01 19:41:46 GMT
//
// Description: This module serves as a testbench for the sc_nadder module.
// For more information on stochastic computing: https://en.wikipedia.org/wiki/Stochastic_computing
//////////////////////////////////////////////////////////////////////////////////
`timescale 1ns / 10ps

module alaghi_nadder_tb();
   parameter INPUT_STREAMS = 31;

   reg clk;
   reg rst;
   reg [INPUT_STREAMS-1:0] inpts;
   wire                    out;

	// Clock Generation
   parameter CLOCK_PERIOD=10;
   initial clk=1;
   always begin
      #(CLOCK_PERIOD/2);
      clk = ~clk;
   end 

   alaghi_nadder dut(.clk(clk), .rst(rst), .inpts(inpts), .out(out));

   initial begin
      // initialize inputs
      rst = 1;
      inpts = 0;

      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      rst = 0; inpts = 31'b1111111111111111111111111111111; 
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);
      @(posedge clk);

		

      $stop;
   end
endmodule
