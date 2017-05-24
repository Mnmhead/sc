module sc_dot_product_sim();
   parameter DIMENSION = 4;
   parameter WIDTH     = 8;
   
   reg                       clk;
   reg                       rst;
   reg [WIDTH*DIMENSION-1:0] datas;
   reg [WIDTH*DIMENSION-1:0] weights;

   // Instantiate noise sources. Only two are required, only multipliers
   // required uncorrelated streams.
   reg [WIDTH-1:0] rng0;
   lfsr1 LFSR1(.clk(clk), .rst(rst), .seed(xxx), .enable(1), .restart(0), .out(rng0));
   reg [WIDTH-1:0] rng1;
   lfsr2 LFSR2(.clk(clk), .rst(rst), .seed(xxx), .enable(1), .restart(0), .out(rng1)); 

   // Instantiate the SNGs to produce stochastic bitstreams for all
   // data and weights.
   reg [DIMENSION-1:0] s_datas;
   reg [DIMENSION-1:0] s_weights;
   genvar d;
   generate
      for(d = 0; d < DIMENSION; d = d + 1) begin : sng_loop
         sng DATA_SNG(
            .clk(clk), 
            .rst(rst), 
            .in(datas[d*WIDTH +: WIDTH]), 
            .rng(rng0),
            .out(s_datas[d])
         );
         sng WEIGHT_SNG(
            .clk(clk), 
            .rst(rst), 
            .in(weights[d*WIDTH +: WIDTH]), 
            .rng(rng1),
            .out(s_weights[d])
         );
      end
   endgenerate

   // Generate a select stream for the adder.
   reg [clogb2(DIMENSION)-1:0] sel;
   counter COUNTER(.clk(clk), .rst(rst), .enable(1), .restart(0), .out(sel));

   // Instantiate the dot product module
   reg test_rst;
   wire result;
   wire valid;
   sc_dot_product DOT_PRODUCT(
      .clk(clk), 
      .rst(rst), 
      .data(s_datas), 
      .weights(s_weights), 
      .sel(sel), 
      .result(result), 
      .valid(valid)
   );

   // Pipe the result into a sd convertor as soon as valid goes high
   wire [WIDTH-1:0] non_scaled_binary_result;
   reg in_stream;
   reg [WIDTH:0] last_counter; 
   reg last;
   always @(posedge clk) begin
      if( valid == 1'b1 ) begin
         if( last_counter[WIDTH] == 1'b1 ) begin
            last <= 1;
            last_counter <= 0;
         end else begin
            last <= 0;
            last_counter <= last_counter + 1;
         end
         
         in_stream <= result;
      end else begin
         in_stream <= 0;
         last_counter <= 0;
      end
   end

   sd_converter SD_CONVERTER(
      .clk(clk), 
      .rst(rst), 
      .in(in_stream), 
      .last(last), 
      .out(non_scaled_binary_result)
   );
   
   wire [(WIDTH*2) + clogb2(DIMENSION) - 1:0] dot_product;
   // what the heck....how do I scale the product back up to normal values
   assign dot_product = non_scaled_binary_result * clogb2(DIMENSION) * WIDTH // or 2 ** log2(WIDTH)

endmodule // sc_dot_product_sim
