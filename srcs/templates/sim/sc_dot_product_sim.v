module sc_dot_product_sim();
   parameter DIMENSION = 4;
   parameter WIDTH     = 8;
   
   reg                       clk;
   reg                       rst;
   reg [WIDTH*DIMENSION-1:0] datas;
   reg [WIDTH*DIMENSION-1:0] weights;

   // Clock Generation
   parameter CLOCK_PERIOD=10;
   initial clk=1;
   always begin
      #(CLOCK_PERIOD/2);
      clk = ~clk;
   end 

   // 15 15 15 15
   initial datas = 32'b00001111 00001111 00001111 00001111;
   // 10 10 10 10
   initial weights = 32'b00001010 00001010 00001010 00001010;

   integer expected_result;
   initial expected_result = 600;

   // Instantiate noise sources. Only two are required, only multipliers
   // required uncorrelated streams.
   
   reg [WIDTH-1:0] seed1;
   reg [WIDTH-1:0] seed2;
   initial seed1 = 8'b11110011;
   initial seed2 = 8'b00110001;

   reg [WIDTH-1:0] rng0;
   lfsr1 LFSR1(.clk(clk), .rst(rst), .seed(seed1), .enable(1), .restart(0), .out(rng0));
   reg [WIDTH-1:0] rng1;
   lfsr2 LFSR2(.clk(clk), .rst(rst), .seed(seed2), .enable(1), .restart(0), .out(rng1)); 

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
   //reg [clogb2(DIMENSION)-1:0] sel;
   reg [2-1:0] sel;
   counter COUNTER(.clk(clk), .rst(rst), .enable(1), .restart(0), .out(sel));

   // Instantiate the dot product module
   //reg test_rst;
   wire result;
   reg valid;
   initial valid = 0; 
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
   reg [WIDTH-1:0] last_counter; // 8 bit
   reg last;
   initial last_counter = 0;
   initial last = 0;
   always @(posedge clk) begin
      if(rst == 1) begin
         last_counter <= 0;
         last <= 0;
         in_stream <= 0;
      end else if( valid == 1'b1 ) begin
         if( last_counter == 8'b11111111 ) begin
            last <= 1;
            last_counter <= 0;
         end else begin
            last <= 0;
            last_counter <= last_counter + 1;
         end
         
         in_stream <= result;
      end else begin
         last_counter <= 0;
         last <= 0;
         in_stream <= 0;
      end
   end

   sd_converter SD_CONVERTER(
      .clk(clk), 
      .rst(rst), 
      .in(in_stream), 
      .last(last), 
      .out(non_scaled_binary_result)
   );

   //wire [(WIDTH*2) + clogb2(DIMENSION) - 1:0] dot_product;
   //assign dot_product = non_scaled_binary_result * 2^clogb2(DIMENSION) * WIDTH // or 2 ** log2(WIDTH)
   wire [17:0] dot_product;
   assign dot_product = non_scaled_binary_result * 4 * 8;
 
   wire done;
   assign done = (last == 1'b1);

   always @(*) begin
      if(done) begin
         $display("expected result = %d\n actual result = %d\n", expected_result, dot_product );
         $display("DONE!\n" );
      end
   end

endmodule // sc_dot_product_sim
