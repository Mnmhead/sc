module shift_register(clk, rst, data_in, data_out, shift);

   parameter DEPTH = 1;
   parameter DATA_WIDTH = 8;

   input clk;
   input rst;
   input [DATA_WIDTH-1:0] data_in;
   output [DATA_WIDTH-1:0] data_out;
   input 		   shift;
         
   genvar i;

   reg [DATA_WIDTH-1:0] internal_registers [DEPTH-1:0];

   //assign first register
   always @ (posedge clk) begin
      if (rst == 1)
	internal_registers[0] <= 0;
      else if (shift == 1)
	internal_registers[0] <= data_in;
      else
	internal_registers[0] <= internal_registers[0];
   end

   generate
      for (i = 1; i < DEPTH; i = i + 1) begin: sr_loop
	 always @ (posedge clk) begin
	    if (rst == 1)
	      internal_registers[i] <= 0;
	    else if (shift == 1)
	      internal_registers[i] <= internal_registers[i-1];
	    else
	      internal_registers[i] <= internal_registers[i];
	 end
      end
   endgenerate

   assign data_out = internal_registers[DEPTH-1];
      
endmodule // shift_register
