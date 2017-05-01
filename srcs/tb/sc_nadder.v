//////////////////////////////////////////////////////////////////////////////////
// Create Date: 2017-05-01 19:41:46 GMT
//
// Description: The circuit represents a multi-input adder in the stochastic domain.
// For more information on stochastic computing: https://en.wikipedia.org/wiki/Stochastic_computing
//
// Requirements:
// The number of input streams must be a power of 2. The input 'sel' must
// be the concatenation of log2(INPUT_STREAMS) number of un-correlated stochastic streams
// (each with value=0.5).
//////////////////////////////////////////////////////////////////////////////////
`timescale 1ns / 10ps

module sc_nadder_tb();
   parameter INPUT_STREAMS = 8;
   parameter SELECT_WIDTH = 3;

   reg [INPUT_STREAMS-1:0] x;
   reg [SELECT_WIDTH-1:0]  sel;
   wire                    out;

   sc_nadder dut(.x(x), .sel(sel), .out(out));

   integer errors;
   initial errors = 0;
   
    integer i;
    integer s;
   initial begin
      // initialize inputs
      x = 0;
      sel = 0;
      #25;

      // for all 256 input stream permutations, test each possible select permutation
      for(i = 0; i < 256; i = i + 1) begin
         x = i;
         for(s = 0; s < 8; s = s + 1) begin
            sel = s;
            #5;
            //if( x[s] != out ) begin
               $display( "Error incorrect output. Input streams: %B, Select streams: %B, out: %d\n", x, sel, out );
               errors = errors + 1;
            //end
            #5;
         end
      end

      // error summary
      if( errors > 0 ) begin
          $display("Validataion failure: %d error(s).", errors);
      end else begin
            $display("Validation successful.");
      end

      $stop;
   end
endmodule // sc_nadder_tb
