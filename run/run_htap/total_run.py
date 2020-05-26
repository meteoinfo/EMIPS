"""
Process emission data by spatial allocation, temporal allocation
and chemical speciation.
"""

#Set current working directory
from inspect import getsourcefile
dir_run = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
if not dir_run in sys.path:
    sys.path.append(dir_run)
dir_inter = r'D:\run_data\emips\run_htap\inter_data'

import emission_htap_2010 as emission

#Set year month
year = 2010
month = 1

#Process emission data except VOC
print('Process emission data except VOC...')
import run_pollutants
run_pollutants.run(year, month, dir_inter, emission)

#Process emission data of VOC
print('\n#####################################')
print('Process emission data of VOC...')
import run_VOC
run_VOC.run(year, month, dir_inter, emission)

#Lump voc according chemical mechanism
print('\n#####################################')
print('Lump voc according chemical mechanism...')
#Using RADM2 chemical mechanism
from emips.chem_spec import RADM2
import lump_VOC
lump_VOC.run(year, month, dir_inter, RADM2())

#Merge all pollutant emission files in one file for each sector
print('\n#####################################')
print('merge all pollutant emission files in one file for each sector...')
import merge_sector
merge_sector.run(year, month, dir_inter)