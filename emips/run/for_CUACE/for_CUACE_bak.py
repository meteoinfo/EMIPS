"""
# Author: Wencong Chen
# Date: 2022-11-27
# Purpose: Convert netcdf model-ready emission file to GrADS data format for CUACE model 
           and write the description file of the output binary data files.
"""
import time
time_start = time.time()
#Set current working directory
from inspect import getsourcefile
dir_run = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
if not dir_run in sys.path:
    sys.path.append(dir_run)

#set year and months
year = 2017
months = [1]
##Set directory for input and output files
dir_in = r'G:\test'
dir_out = r'G:\test'
#Set dimension length of output file.
xn = 324
yn = 180
xmin = 64.0
ymin = 15.0
xdelta = 0.25
ydelta = 0.25

print('Convert to grads...')
import convert_grads
convert_grads.run(year, months, dir_in, dir_out, xn, yn)

print('Write .ctl files...')
import write_ctl
write_ctl.run(year, months, dir_out, xn, yn, xmin, ymin, xdelta, ydelta)

print('-------------------')
print('---All finished!---')
print('-------------------')
time_end = time.time()
time = (time_end - time_start) / 60
print('Time: {:.2f}min'.format(time))
