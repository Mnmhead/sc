//////////////////////////////////////////////////////////////////////////////////
// Credit Vincent Lee
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
   parameter LENGTH = 4
) (
   clk,
   rst,
   data,
   weights,
   sel,
   result
);

   // Helper function to set the number of select streams needed
   function integer clogb2;
      input [31:0] value;
      begin
         value = value - 1;
         for (clogb2 = 0; value > 0; clogb2 = clogb2 + 1) begin
            value = value >> 1;
         end
      end
   endfunction

   parameter SELECT_WIDTH = clogb2(LENGTH)

   // inputs and outputs
   input                    clk;
   input                    rst;
   input [LENGTH-1:0]       data;
   input [LENGTH-1:0]       weights;
   input [SELECT_WIDTH-1:0] sel;
   output                   result;

   // multipication modules, for element wise multiplication of data and weights
   genvar i;
   wire [LENGTH-1:0] mult_out;
   generate
      for( i = 0; i < LENGTH; i = i + 1) begin : mult
         sc_multiplier(.x(data[i]), .y(weights[i]), .res(mult_out[i]));
      end
   endgenerate

   // direct multiplication output to an intermediate register
   reg [LENGTH-1:0] product_streams;
   always @(posedge clk) begin
      product_streams <= mult_out;
   end

   // add all element-wise products
   sc_nadder #(LENGTH) (.x(product_streams), .sel(sel), .out(result));

endmodule // sc_dot_product
