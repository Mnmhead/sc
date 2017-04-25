//////////////////////////////////////////////////////////////////////////////////
// Author: Vincent Lee
// Create Date: 04/21/2017 6:28pm
//
// Description: A non-conventional stochastic adder. Intellectual property of Armin Alaghi.
// For more information on stochastic computing: 
// https://en.wikipedia.org/wiki/Stochastic_computing
//////////////////////////////////////////////////////////////////////////////////

module alaghi_adder(clk, rst, x, y, out);
   parameter reset_seed = 0;

   input clk;
   input rst;
   input x;
   input y;
   output out;

   wire   xor_input = x ^ y;
   
   reg 	  tff;
   always @ (posedge clk) begin
      if (rst == 1) begin
	 tff <= reset_seed;
      end else if (xor_input == 1) begin
	 tff <= ~tff;
      end else begin
	 tff <= tff;
      end
   end

   assign out = (xor_input == 1) ? tff : y;
   
endmodule // alaghi_adder
