module counter_n_bit #(
   parameter N = 10,
   parameter BOUND = 1000 // the upper bound of the range of this counter
) (
   input clk,
   input rst,
   input enable,
   input restart,
   output [N-1:0] out
);

   reg [N-1:0] counter;
   always @(posedge clk or posedge rst) begin
      if (rst) counter <= 0;
      else if (restart) counter <= 0;
      else if (enable) begin
         if (counter == BOUND) counter <= 0;
         else counter <= counter + 1;
      end
   end

   // optional reverse code
   // genvar i;
   // generate
   //    for(i=0; i<10;i=i+1) assign out[i] = counter[N-1-i];
   // endgenerate

endmodule // counter_n_bit
