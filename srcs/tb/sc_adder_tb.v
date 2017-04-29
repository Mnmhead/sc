//////////////////////////////////////////////////////////////////////////////////
// Copyright (c) Gyorgy Wyatt Muntean 2017
// Create Date: 04/29/2017 4:12pm
//
// Description: Testbench for sc_adder module. 
//////////////////////////////////////////////////////////////////////////////////
`timescale 1ns / 10ps

module sc_adder_tb();
	reg x;
	reg y;
	reg sel;
	wire out;

	sc_adder dut( .x(x), .y(y), .sel(sel), .out(out) );

	initial begin
		// initialize inputs
		x = 0;
		y = 0;
		sel = 0;

		#100;

		// run through all combinations of inputs
		x = 0; y = 0; sel = 0; 
		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
		end
		#10;

		x = 0; y = 0; sel = 1;
		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
		end
		#10;

		x = 0; y = 1; sel = 0;
		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
		end
		#10;

		x = 0; y = 1; sel = 1;
		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
		end
		#10;

		x = 1; y = 0; sel = 0;
		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
		end
		#10;

		x = 1; y = 0; sel = 1;
		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
		end
		#10;

		x = 1; y = 1; sel = 0;
		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
		end
		#10;

		x = 1; y = 1; sel = 1;
		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
		end
		#10;

		$stop;	
	end
endmodule // sc_adder_tb
