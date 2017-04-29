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

    integer errors;
    initial errors = 0;
	initial begin
		// initialize inputs
		x = 0;
		y = 0;
		sel = 0;
		#25;

		// run through all combinations of inputs
		x = 0; y = 0; sel = 0; #5;
		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
			errors = errors + 1;
		end
		#5;

		x = 0; y = 0; sel = 1; #5;
		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
			errors = errors + 1;
		end
		#5;

		x = 0; y = 1; sel = 0; #5;
		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
			errors = errors + 1;
		end
		#5;

		x = 0; y = 1; sel = 1; #5;
		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
			errors = errors + 1;
		end
		#5;

		x = 1; y = 0; sel = 0; #5;
		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
			errors = errors + 1;
		end
		#5;

		x = 1; y = 0; sel = 1; #5;
		if( out != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
			errors = errors + 1;
		end
		#5;

		x = 1; y = 1; sel = 0; #5;
		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
			errors = errors + 1;
		end
		#5;

		x = 1; y = 1; sel = 1; #5;
		if( out != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, sel %d\n", x, y, sel);
			errors = errors + 1;
		end
		#5;
		
		if( errors > 0 ) begin
		    $display("Validataion failure: %d error(s).", errors);
		end else begin
            $display("Validation successful.");
        end

		$stop;	
	end
endmodule // sc_adder_tb
