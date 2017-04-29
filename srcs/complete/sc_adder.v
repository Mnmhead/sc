//////////////////////////////////////////////////////////////////////////////////
// Copyright (c) Gyorgy Wyatt Muntean 2017
// Create Date: 04/10/2017 4:12pm
//
// Description: The circuit represents an adder in the stochastic domain. 
// For more information on stochastic computing: 
// https://en.wikipedia.org/wiki/Stochastic_computing
//
// Requirement: The input, 'sel', must be a stochastic bitstream where probability of
// a 1 or 0 is equally 0.5.
//
//////////////////////////////////////////////////////////////////////////////////

module sc_adder(
   input x,
   input y,
   input sel,
   output out
)

   assign out = (sel == 0) ? x : y;

endmodule // sc_adder
