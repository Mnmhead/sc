//////////////////////////////////////////////////////////////////////////////////
// Copyright (c) Gyorgy Wyatt Muntean 2017
// Create Date: 04/10/2017 4:12pm
//
// Description: The circuit represents a multiplier in the stochastic domain. 
// For more information on stochastic computing: 
// https://en.wikipedia.org/wiki/Stochastic_computing
//
// Note: bi-polar representation [-1,1]
//
//////////////////////////////////////////////////////////////////////////////////

module sc_multiplier_bi( 
   x,  
   y,  
   z   
);

   input x;
   input y;
   output z;

   assign z = ~(x ^ y);
endmodule
