"""
-----CAMS-----
Process emission data by spatial allocation, temporal allocation
and chemical speciation.
"""

import os
import sys

#Set current working directory
from inspect import getsourcefile
dir_run = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
if not dir_run in sys.path:
    sys.path.append(dir_run)

import emission_cams_year as emission
from emips.spatial_alloc import GridDesc

def run_cams(year, months, model_grid, mechanism_name, mechanism):
    """
    Process CAMS emission data by spatial allocation, temporal allocation
    and chemical speciation.

    :param year: (*int*) Year.
    :param months: (*list*) Months.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param mechanism_name: (*string*) mechanism's name.
    :param mechanism: (*ChemicalMechanism*) Chemical mechanism.
    """
    print('------------------------------------')
    print('-----Processing CAMS data.....------')
    print('------------------------------------')
    for month in months:
        print('##########')
        print('Month: {}'.format(month))
        print('##########')
        
        dir_inter = os.path.join(r'G:\test_data', mechanism_name, r'region_0.15\CAMS\{0:}\{0:}{1:>02d}'.format(year, month))
        if not os.path.exists(dir_inter):
            os.mkdir(dir_inter)
        
        #Process emission data except VOC
        print('Process emission data except VOC...')
        import run_pollutants
        run_pollutants.run(year, month, dir_inter, emission, model_grid)
        
        #Process emission data of VOC
        print('\n#####################################')
        print('Process emission data of VOC...')
        import run_VOC
        run_VOC.run(year, month, dir_inter, emission, model_grid)
        
        #Lump voc according chemical mechanism
        print('\n#####################################')
        print('Lump voc according chemical mechanism...')
        import lump_VOC
        lump_VOC.run(year, month, dir_inter, mechanism, model_grid)
        
        #Merge all pollutant emission files in one file for each sector
        print('\n#####################################')
        print('merge all pollutant emission files in one file for each sector...')
        import merge_sector
        merge_sector.run(year, month, dir_inter, model_grid)
        
    print('-------------------------------')
    print('-----CAMS data completed!------')
    print('-------------------------------')