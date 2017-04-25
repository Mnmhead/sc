//////////////////////////////////////////////////////////////////////////////////
// Author: Gyorgy Wyatt Muntean 2017
// Create Date: 04/24/2017 6:26pm
//
// Description: The circuit represents a dot product of two vectors in the stochastic domain.
// For more information on stochastic computing: 
// https://en.wikipedia.org/wiki/Stochastic_computing
//
// Requirement: The inputs, 'sel', must be stochastic bitstreams where probability of
// a 1 or 0 is equally 0.5.
//
//////////////////////////////////////////////////////////////////////////////////

module sc_dot_product #(
   parameter LENGTH = 3
) (
   input clk,
   input rst,
   input [LENGTH-1:0] data,
   input [LENGTH-1:0] weights,
   input [LENGTH-1:0] sel,
   output result
);

   // multipication modules, for element wise multiply of data and weights
   genvar i;
   wire [LENGTH-1:0] product_stream;
   generate
      for( i = 0; i < LENGTH; i = i + 1) begin : mult
         sc_multiplier(.x(data[i]), .y(weights[i]), .res(product_stream[i]));
      end
   endgenerate

   // add all element wise products
   sc_n_adder_chain #(LENGTH) (.clk(clk),
                               .rst(rst),
                               .inputs(product_stream),
                               .sel(sel),
                               .sum(result));

endmodule // sc_dot_product
