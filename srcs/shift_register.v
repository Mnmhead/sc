//////////////////////////////////////////////////////////////////////////////////
// Credit Vincent Lee
// Create Date: 04/29/2017 5:23pm
//
// Description: The circuit represents a 1-bit width shift register.
// Depth is parameterizeable by the parameter DEPTH.
//////////////////////////////////////////////////////////////////////////////////

module shift_register #(
   parameter DEPTH = 1
) (
   input clk, 
   input rst, 
   input data_in, 
   output data_out
);

   reg internal_registers [DEPTH-1:0];

   // assign first register
   always @ (posedge clk) begin
      if (rst == 1)
	      internal_registers[0] <= 0;
      else
	      internal_registers[0] <= data_in;
   end

   genvar i;
   generate
      for (i = 1; i < DEPTH; i = i + 1) begin: sr_loop
	      always @ (posedge clk) begin
	         if (rst == 1)
	            internal_registers[i] <= 0;
	         else
                internal_registers[i] <= internal_registers[i-1];
	      end
      end
   endgenerate

   assign data_out = internal_registers[DEPTH-1];
endmodule // shift_register
