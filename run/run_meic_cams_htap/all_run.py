"""
Process emission data and merge EMIPS output emission data(MEIC, CAMS, HTAP).
"""

import time
time_start = time.time()

#Set current working directory
from inspect import getsourcefile
dir_run = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
if not dir_run in sys.path:
    sys.path.append(dir_run)

from mipylib import geolib
from emips.spatial_alloc import GridDesc

#set parameters
from emips.chem_spec import MOZART_wrfchem as mechanism
year = 2017
months = [1]
mechanism_name = 'mozart'

#Set model grids
proj = geolib.projinfo()
model_grid = GridDesc(proj, x_orig=70., x_cell=0.15, x_num=502,
    y_orig=15., y_cell=0.15, y_num=330)

#process MEIC data
from meic import total_run_meic
total_run_meic.run_meic(year, months, model_grid, mechanism_name, mechanism())

#process HTAP data
from htap import total_run_htap
total_run_htap.run_htap(months, model_grid, mechanism_name, mechanism())

#process CAMS data
from cams import total_run_cams
total_run_cams.run_cams(year, months, model_grid, mechanism_name, mechanism())

#merge output data
from merge_meic_cams_htap import merge_output
merge_output(year, months, model_grid, mechanism_name)

print('-------------------------------')
print('---All processing completed!---')
print('-------------------------------')

#Calculate running time
time_end = time.time()
time = (time_start - time_end)/60
print('Time: {}'.format(time)