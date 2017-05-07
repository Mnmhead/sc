module lsfr_n_bit #(
   parameter N = 32
) (
   input clk,
   input rst,
   input [N-1:0] seed,
   input enable,
   input restart,
   output [N-1:0] data
);

   reg [N-1:0] shift_reg;
   wire shift_in;

   always @(posedge clk or pasedge rst) begin
      if (rst) shift_reg <= seed;
      else if (restart) shift_reg <= seed;
      else if (enable) shift_reg <= {shift_reg[N-2:0], shift_in};
   end

   wire xor_out;
   assign xor_out = shift_reg[2] ^ shift_reg[1];

   // optional zero detector code
   wire zero_detector;
   assign zero_detector = ~(|(shift_reg[38:0]));
   assign shift_in = xout_out ^ zero_detector;

   assign data = shift_reg;

endmodule // lfsr_n_bit
