"""
# Author: Wencong Chen
# Date: 2022-08-04
# Purpose: Convert netcdf model-ready emission file to GrADS data format for CUACE model 
           and write the description file of the output binary data files.
"""

#Set current working directory
from inspect import getsourcefile
dir_run = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
if not dir_run in sys.path:
    sys.path.append(dir_run)

#set year and months
year = 2017
months = [1,2]
##Set directory for input and output files
dir_in = r'D:\test'
dir_out = r'D:\test'
#Set dimension length of output file.
xn = 1440
yn = 720

print('Convert to grads...')
import convert_grads
convert_grads.run(year, months, dir_in, dir_out, xn, yn)
print('Write .ctl files...')
import write_ctl
wrtie_ctl.run(year, months, dir_out)

print('-------------------')
print('---All finished!---')
print('-------------------')

