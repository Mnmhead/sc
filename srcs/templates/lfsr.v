//////////////////////////////////////////////////////////////////////////////////
// Credit to Vincent Lee
// Create Date: 04/10/2017 6:25pm
//
// Description: LFSR module.
//
// Parameters: The DATA_WIDTH parameter controls the datawidth of the output.
// Valid data widths are 3-20,24, and 32.
//
//////////////////////////////////////////////////////////////////////////////////

module lfsr(
   parameter DATA_WIDTH = 8
) (
   input clk, 
   input rst, 
   output [DATA_WIDTH-1:0] out
);

   genvar 		   i;

   reg [DATA_WIDTH-1:0]    shift_regs;
   wire 		   feedback;

   //brute force the hardcoded taps
   assign feedback = (DATA_WIDTH == 3) ? shift_regs[2] ^ shift_regs[1] :
		     (DATA_WIDTH == 4) ? shift_regs[3] ^ shift_regs[2] :
		     (DATA_WIDTH == 5) ? shift_regs[4] ^ shift_regs[2] :
		     (DATA_WIDTH == 6) ? shift_regs[5] ^ shift_regs[4] :
		     (DATA_WIDTH == 7) ? shift_regs[6] ^ shift_regs[5] :
		     (DATA_WIDTH == 8) ? shift_regs[7] ^ shift_regs[6] ^ shift_regs[5] ^ shift_regs[0] :
		     (DATA_WIDTH == 9) ? shift_regs[8] ^ shift_regs[4] :
		     (DATA_WIDTH == 10) ? shift_regs[9] ^ shift_regs[8] :
		     (DATA_WIDTH == 11) ? shift_regs[10] ^ shift_regs[6] :
		     (DATA_WIDTH == 12) ? shift_regs[11] ^ shift_regs[10] ^ shift_regs[9] ^ shift_regs[3] :
		     (DATA_WIDTH == 13) ? shift_regs[12] ^ shift_regs[11] ^ shift_regs[10] ^ shift_regs[7] :
		     (DATA_WIDTH == 14) ? shift_regs[13] ^ shift_regs[12] ^ shift_regs[11] ^ shift_regs[1] :
		     (DATA_WIDTH == 15) ? shift_regs[14] ^ shift_regs[13] :
		     (DATA_WIDTH == 16) ? shift_regs[15] ^ shift_regs[14] ^ shift_regs[12] ^ shift_regs[3] :
		     (DATA_WIDTH == 17) ? shift_regs[16] ^ shift_regs[13] :
		     (DATA_WIDTH == 18) ? shift_regs[17] ^ shift_regs[10] :
		     (DATA_WIDTH == 19) ? shift_regs[18] ^ shift_regs[17] ^ shift_regs[16] ^ shift_regs[13] :
		     (DATA_WIDTH == 20) ? shift_regs[19] ^ shift_regs[16] :
		     (DATA_WIDTH == 24) ? shift_regs[23] ^ shift_regs[22] ^ shift_regs[21] ^ shift_regs[16] :
		     (DATA_WIDTH == 32) ? shift_regs[31] ^ shift_regs[30] ^ shift_regs[29] ^ shift_regs[9] :
		     0;
   
   // shifting logic
   generate
      for (i = 0; i < DATA_WIDTH; i = i + 1) begin: lfsr_loop
	 // always insert a 1 in the front on reset
	 if (i == 0) begin
	    always @ (posedge clk) begin
	       if (rst == 1) shift_regs[i] <= 1;
	       else shift_regs[i] <= feedback;
	    end
	 end
	 //shift everything else
	 else begin
	    always @ (posedge clk) begin
	       if (rst == 1) shift_regs[i] <= 0;
	       else shift_regs[i] <= shift_regs[i-1];
	    end	    
	 end
      end
   endgenerate

   assign out = shift_regs;
   
endmodule // lfsr
