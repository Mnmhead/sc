# Copyright (c) Gyorgy Wyatt Muntean 2017
# This file contains common code shared throughout the generation scripts in this repo.

import math
from time import gmtime, strftime

# Writes string to file f with numTabs number of tabs before
# the string and a newline character after the string.
def write_line( f, string, numTabs=0 ):
   tab = ""
   for i in range(0,numTabs):
      tab += "   "
   f.write( tab + string + "\n" )

# Function to get the time and date in GMT
# Value returned as a string
def get_time():
   return strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " GMT"

# Computes the ceiling log base 2 of input.
def clogb2( x ):
   return int(math.ceil( math.log( x, 2 ) ))