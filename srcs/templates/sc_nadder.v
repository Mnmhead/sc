//////////////////////////////////////////////////////////////////////////////////
// Credit Vincent Lee
// Create Date: 04/21/2017 5:17pm
//
// Description: The circuit represents a multi-input adder in the stochastic domain.
// For more information on stochastic computing: https://en.wikipedia.org/wiki/Stochastic_computing
//
// Parameters:
// The number of inputs to the adder is parameterizable by setting INPUT_STREAMS
// to the number of inputs.
//
// Requirements:
// The number of input streams must be a power of 2. The input 'sel' must
// be the concatenation of log2(INPUT_STREAMS) number of un-correlated stochastic streams 
// (each with value=0.5).
//
//////////////////////////////////////////////////////////////////////////////////

module sc_nadder #(
   parameter INPUT_STREAMS = 2
) (
   x,
   sel,
   out
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

   parameter SELECT_WIDTH = clogb2(INPUT_STREAMS)

   input [INPUT_STREAMS-1:0] x;
   input [SELECT_WIDTH-1:0]  sel;
   output                    out;

   assign out = x[sel];

endmodule // sc_nadder
