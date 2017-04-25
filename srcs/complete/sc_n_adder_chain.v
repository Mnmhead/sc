//////////////////////////////////////////////////////////////////////////////////
// Author: Gyorgy Wyatt Muntean 2017
// Create Date: 04/24/2017 6:09pm
//
// Description: The circuit represents a chain of n adders in the stochastic domain. 
// For more information on stochastic computing: 
// https://en.wikipedia.org/wiki/Stochastic_computing
//
// Requirement: The inputs, 'sel', must be stochastic bitstreams where probability of
// a 1 or 0 is 0.5.
//
//////////////////////////////////////////////////////////////////////////////////

module sc_n_adder_chain #(
   parameter N = 2
) ( 
   input clk,
   input rst,
   input [N-1:0] inputs, // N inputs
   input [N-2:0] sel,    // N-1 select streams
   output sum
);

   wire [N-3:0] shifted_element;
   genvar shift;
   generate
      // shift n-2 inputs (first two inputs are fed directly into adder).
      for(shift = 2; shift < N; shift = shift + 1) begin : shiftReg
         shift_register SHIFT(.clk(clk), 
                              .rst(rst), 
                              .data_in(inputs[i]), 
                              .data_out(shifted_element[shift-2]), 
                              .shift(i-1));
   endgenerate

   // add first two elements
   wire [N-2:0] i_sum; // intermediate sums (N-1 intermediate wires)
   sc_adder INIT_ADDER(.x(inputs[0]), .y(inputs[1]), .sel(sel[0]), .out(i_sum[0]));
   
   genvar i;
   generate 
      // add the remaining N-2 inputs
      for(i = 0; i < N-2; i = i + 1) begin : ADDER_CHAIN
         sc_adder ADDER(.x(i_sum[i]),
                        .y(shifted_element[i]),
                        .sel(sel[i+1]),
                        .out(i_sum[i+1]));
      end
   endgenerate
   
   assign sum = i_sum[N-2]; // assign the last intermediate output to the output of this module
endmodule // n_adder_chain
