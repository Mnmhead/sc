//////////////////////////////////////////////////////////////////////////////////
// Credit to Vincent Lee
// Create Date: 04/10/2017 5:51pm
//
// Description: The module represents a stochastic number generator.
// This is essentially just a wrapper for a digital to stochastic converter. 
// We just package a noise source in this module as well (LFSR only).
// For more information on stochastic computing: 
// https://en.wikipedia.org/wiki/Stochastic_computing
//////////////////////////////////////////////////////////////////////////////////

module sng #(
   parameter PRECISION = 8
) ();
   input clk;
   input rst;
   input [PRECISION-1] in;
   output out;

   // instantiate an LFSR with the proper precision
   wire [PRECISION-1:0] rng;
   lfsr LFSR #(PRECISION)(.clk(clk), .rst(rst), .out(rng));   

   // pass the LFSR's input to the convertor and clock the output
   reg ds_out [1:0];
   ds_converter DS_CONVERT #(PRECISION)(.in(in), .rng(rng), .out(ds_out[0]));

   always @(posedge clk) begin
      if (rst == 1) begin
         ds_out[0] = 0;
         ds_out[1] = 0;
      end else begin
         ds_out[1] <= ds_out[0];
      end
   end

   assign out = ds_out[1];

endmodule // sng
