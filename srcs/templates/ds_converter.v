//////////////////////////////////////////////////////////////////////////////////
// Credit to Vincent Lee
// Create Date: 04/10/2017 5:51pm
//
// Description: The module represents a digital to stochastic converter.
// For more information on stochastic computing: 
// https://en.wikipedia.org/wiki/Stochastic_computing
//
// Note: Conversion is from digital to stochastic uni-polar representation.
// The range of each stochastic bitstream produced is [0,1].
//
//////////////////////////////////////////////////////////////////////////////////

module ds_converter #(
   parameter PRECISION = 8;
) ( 
   input [PRECISION-1:0] in, 
   input [PRECISION-1:0] rng, 
   output out
);

   assign out = (rng < in) ? 1 : 0;

endmodule // ds_converter
