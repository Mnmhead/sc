//////////////////////////////////////////////////////////////////////////////////
// Credit Armin Alaghi
// Create Date: 04/29/2017 4:12pm
//
// Description: Testbench for alaghi_adder module. 
//////////////////////////////////////////////////////////////////////////////////
`timescale 1ns / 10ps

module alaghi_adder_tb();
   reg clk;
	reg rst;
	reg x;
   reg y;
	wire out;

    // Clock Generation
   parameter CLOCK_PERIOD=10;
   initial clk=1;
   always begin
      #(CLOCK_PERIOD/2);
      clk = ~clk;
   end

	alaghi_adder dut( .clk(clk), .rst(rst), .x(x), .y(y), .out(out) );

   integer errors;
   initial errors = 0;
	initial begin
		// initialize inputs
      rst = 1;
		x = 0;
		y = 0;
		#(4*CLOCK_PERIOD);


		// run through a sweep of inputs to give the toggle flip time some time
		// to do its thing.
      rst = 0; @(posedge clk)
		x = 0; y = 0; @(posedge clk)

		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d\n", x, y);
			errors = errors + 1;
		end

		x = 1; y = 0; @(posedge clk)

		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, out: %d\n", x, y, out);
			errors = errors + 1;
		end

		x = 1; y = 0; @(posedge clk)
		x = 1; y = 0; @(posedge clk)
		x = 1; y = 0; @(posedge clk)
		x = 1; y = 0; @(posedge clk)
		x = 1; y = 0; @(posedge clk)
		x = 0; y = 0; @(posedge clk)
		x = 0; y = 0; @(posedge clk)
		x = 0; y = 0; @(posedge clk)
		x = 0; y = 0; @(posedge clk)
/*
		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d\n", x, y);
			errors = errors + 1;
		end

		x = 0; y = 1; @(posedge clk)

		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d\n", x, y);
			errors = errors + 1;
		end

		x = 1; y = 1; @(posedge clk)

		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d\n", x, y);
			errors = errors + 1;
		end

		x = 0; y = 0; @(posedge clk)

		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d\n", x, y);
			errors = errors + 1;
		end
		*/

		// Error checking.
		if( errors > 0 ) begin
		   $display("Validataion failure: %d error(s).", errors);
		end else begin
         $display("Validation successful.");
      end

		$stop;	
	end
endmodule // alaghi_adder_tb
