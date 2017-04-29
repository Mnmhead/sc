//////////////////////////////////////////////////////////////////////////////////
// Copyright (c) Gyorgy Wyatt Muntean 2017
// Create Date: 04/10/2017 4:12pm
//
// Description: The module represents a stochastic to digital converter.
// For more information on stochastic computing: 
// https://en.wikipedia.org/wiki/Stochastic_computing
//
// Parameters: The PRECISION parameter determines the final precision of the digital
// output (in number of bits).
//
// The input 'last' is used to choose the final length of the stochastic bitstreams
// when converting back to standard digital.
//
//////////////////////////////////////////////////////////////////////////////////

module sd_converter #(
   parameter PRECISION = 8;
) (
   input clk, 
   input rst, 
   input in, 
   input last, 
   output [PRECISION-1:0] out
);

   reg [PRECISION-1:0] count;

   always @ (posedge clk) begin
      if (rst == 1 || last == 1) begin
	      count <= 0;
      end
      else begin
	      count <= count + in;
      end
   end

   assign out = count;

endmodule // sd_converter
