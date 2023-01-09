"""
# Author: Wencong Chen
# Date: 2022-11-27
# Purpose: Process emission data by spatial allocation, temporal allocation
           and chemical speciation(-----CAMS-----).       
"""

import os
import sys
from emips.spatial_alloc import GridDesc
# Set current working directory
from inspect import getsourcefile

dir_run = os.path.dirname(os.path.abspath(getsourcefile(lambda: 0)))
if dir_run not in sys.path:
    sys.path.append(dir_run)

# Import preprocessing scripts
import emission_cams_year as emission


def run(dire, year, months, model_grid, mechanism_name, mechanism):
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

        dir_inter = os.path.join(dire, mechanism_name, r'CAMS\{0:}\{0:}{1:>02d}'.format(year, month))
        # dir_inter = os.path.join(r'G:\emips_data\region_0.1', r'CAMS\{0:}\{0:}{1:>02d}'.format(year, month))
        if not os.path.exists(dir_inter):
            os.makedirs(dir_inter)

        # Process emission data except VOC
        print('Process emission data except VOC...')
        import run_pollutants
        run_pollutants.run(year, month, dir_inter, emission, model_grid)

        # Process emission data of VOC
        print('Process emission data of VOC...')
        import run_VOC
        run_VOC.run(year, month, dir_inter, emission, model_grid)

        # Lump voc according chemical mechanism
        print('Lump voc according chemical mechanism...')
        import lump_VOC
        lump_VOC.run(year, month, dir_inter, mechanism, model_grid)

        # Merge all pollutant emission files in one file for each sector
        print('merge all pollutant emission files in one file for each sector...')
        import merge_sector
        merge_sector.run(year, month, dir_inter, model_grid)

    print('-------------------------------')
    print('-----CAMS data completed!------')
    print('-------------------------------')


if __name__ == '__main__':
    import time

    time_start = time.time()

    # Settings
    year = 2017
    months = [1]
    proj = geolib.projinfo()
    model_grid = GridDesc(proj, x_orig=64., x_cell=0.25, x_num=324,
                          y_orig=15., y_cell=0.25, y_num=180)
    mechanism_name = 'radm2'
    dire = r'G:\test'
    from emips.chem_spec import RADM2_wrfchem as mechanism

    run(dire, year, months, model_grid, mechanism_name, mechanism())

    time_end = time.time()
    time = (time_end - time_start) / 60
    print('Time: {:.2f}min'.format(time))
