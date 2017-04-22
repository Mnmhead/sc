//////////////////////////////////////////////////////////////////////////////////
// Copyright (c) Gyorgy Wyatt Muntean 2017
// Create Date: 04/10/2017 4:12pm
//
// Description: The circuit represents a multiplier in the stochastic domain. 
// For more information on stochastic computing: 
// https://en.wikipedia.org/wiki/Stochastic_computing
//
// Note: uni-polar representation [0,1]
//
//////////////////////////////////////////////////////////////////////////////////

module sc_multiplier( 
   x, 
   y, 
   z 
);

   input x;
   input y;

   assign z = x & y;

   output z;
endmodule
