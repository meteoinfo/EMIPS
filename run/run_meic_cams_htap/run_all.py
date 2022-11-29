"""
# Author: Wencong Chen
# Date: 2022-11-27
# Purpose: Process emission data and merge EMIPS output emission data(MEIC, CAMS, HTAP).
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
from emips.chem_spec import RADM2_wrfchem as mechanism
year = 2017
months = [1]
mechanism_name = 'radm2'

#Set model grids
proj = geolib.projinfo()
model_grid = GridDesc(proj, x_orig=64., x_cell=0.25, x_num=324,
    y_orig=15., y_cell=0.25, y_num=180)
#model_grid = GridDesc(proj, x_orig=70., x_cell=0.1, x_num=751,
#    y_orig=15., y_cell=0.1, y_num=501)
#Set directory
dire = r'G:\test'

#process MEIC data
from meic import total_run_meic
total_run_meic.run(dire, year, months, model_grid, mechanism_name, mechanism())

#process HTAP data
from htap import total_run_htap
total_run_htap.run(dire, months, model_grid, mechanism_name, mechanism())

#process CAMS data
from cams import total_run_cams
total_run_cams.run(dire, year, months, model_grid, mechanism_name, mechanism())

#merge output data
import merge_meic_cams_htap_tw as merge
merge.run(dire, year, months, model_grid, mechanism_name)

print('-------------------------------')
print('-----All process completed!----')
print('-------------------------------')

#Calculate running time
time_end = time.time()
time = (time_end - time_start)/60
print('Time: {}'.format(time))