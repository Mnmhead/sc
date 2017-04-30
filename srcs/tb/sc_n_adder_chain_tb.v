//////////////////////////////////////////////////////////////////////////////////
// Copyright (c) Gyorgy Wyatt Muntean 2017
// Create Date: 04/29/2017 4:58pm
//
// Description: Testbench for sc_adder module. 
//////////////////////////////////////////////////////////////////////////////////
`timescale 1ns / 10ps

module sc_n_adder_chain_tb();
   localparam N = 10;
   reg clk;
   reg rst;
   reg [N-1:0] inputs;
   reg [N-2:0] sel;
   wire sum;

   sc_n_adder_chain #(N) dut( .clk(clk), .rst(rst), .inputs(inputs), .sel(sel), .sum(sum) );

   // Clock generation
   parameter CLOCK_PERIOD=10;
   always begin
      #(CLOCK_PERIOD/2);
      clk = ~clk;
   end 

   initial begin
      // initialize inputs
      rst = 1;
      inputs = 0;
      sel = 0;

      // start sim
      rst = 0;
      inputs = 10'b1111111111;
      sel = 9'b101010010;      


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
                                    

      $stop;
   end
endmodule // sc_n_adder_chain_tb
