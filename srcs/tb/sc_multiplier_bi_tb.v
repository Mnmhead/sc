//////////////////////////////////////////////////////////////////////////////////
// Copyright (c) Gyorgy Wyatt Muntean 2017
// Create Date: 04/29/2017 4:45pm
//
// Description: Testbench for sc_multiplier_bi module. 
//////////////////////////////////////////////////////////////////////////////////
`timescale 1ns / 10ps

module sc_multiplier_bi_tb();
	reg x;
	reg y;
	wire z;

	sc_multiplier_bi dut( .x(x), .y(y), .z(z) );

   integer errors;
   initial errors = 0;
	initial begin
		// initialize inputs
		x = 0;
		y = 0;
		#25;

		// run through all combinations of inputs
		x = 0; y = 0; #5;
		if( z != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, res: %d\n", x, y, z);
			errors = errors + 1;
		end
		#5;

		x = 0; y = 1; #5;
		if( z != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d, res: %d\n", x, y, z);
			errors = errors + 1;
		end
		#5;

		x = 1; y = 0; #5;
		if( z != 0 ) begin
			$display("Error incorrect output. x: %d, y: %d, res: %d\n", x, y, z);
			errors = errors + 1;
		end
		#5;

		x = 1; y = 1; #5;
		if( z != 1 ) begin
			$display("Error incorrect output. x: %d, y: %d, res: %d\n", x, y, z);
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
endmodule // sc_multiplier_tb
