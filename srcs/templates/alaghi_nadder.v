//////////////////////////////////////////////////////////////////////////////////
//
// A perfect tree of alahgi adders. Parameter N must be a power of two.
//
//////////////////////////////////////////////////////////////////////////////////

module alaghi_nadder(
   clk, 
   rst, 
   x, 
   out
);
   parameter N = 16;


   // generate the first layer of the tree.
   // in the python code:
   //    while (a power of 2 fits in N):
   //       find the largest power of 2 that fits within N, call this T
   //       instantiate a tree with a first-level of T/2 adders
   //       N = N - T
   //
   //    if N != 0
   //       we need to create an adder with a 0 input
   //    
   //    for (number of adder trees)
   //       hook up the smallest adder to the next deepest adder (but maintain scale factor)
   //          - add another 0 input until the smallest adder is matching the scale factor of
   //            next deepest adder. 
   //       
   //    when all is said and done, we should have an adder with a scale factor of [1 / 2^(clogb2(N))]

   // do i need to clock the output of each layer of adders?
   // I think I do

   input clk;
   input rst;
   input [N-1:0] x;
   output out;

   // first level of adders
   wire [(N/2)-1:0] out_1;
   genvar i;
   generate
      for(i = 0; i < N; i = i + 2) begin : LEVEL_1
         alaghi_adder(.clk(clk), .rst(rst), .x(x[i]), .y(x[i+1]), .out(out_1[i/2]));
      end
   endgenerate

   reg [(N/2)-1:0] intermediate_out_1;
   always @(posedge clk) begin
      if (rst == 1) begin
         intermediate_out_1 <= 0;
      end else begin
         intermediate_out_1 <= out_1;
      end
   end

   // second level of adders
   wire [(N/4)-1:0] out_2;
   generate
      for(i = 0: i < N/2; i = i + 2) begin : LEVEL_2
         alaghi_adder(.clk(clk), 
                      .rst(rst), 
                      .x(intermediate_out_1[i]), 
                      .y(intermediate_out_1[i+1]), 
                      .out(out_2[i/2]));
      end
   endgenerate

   reg [(N/4)-1:0] intermediate_out_2;
   always @(posedge clk) begin
      if (rst == 1) begin
         intermediate_out_2 <= 0;
      end else begin
         intermediate_out_2 <= out_2;
      end
   end

   // etc. etc. etc. repeat this generation pattern until N=1
   // ...
   // ...


   assign out = intermediate_out_...;

endmodule // alaghi_nadder

