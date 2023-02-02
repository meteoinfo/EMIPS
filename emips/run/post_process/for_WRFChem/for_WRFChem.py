"""
# Author: Wencong Chen
# Date: 2022-08-04
# Purpose: Convert model-ready emission file to meet WRF-Chem's input requirements.
           (height allocation, merge files of different sectors, convert pollutants and projection)
"""
from mipylib import geolib
from emips.spatial_alloc import GridDesc
from emips import ge_data_dir
from emips.utils import SectorEnum
from emips.chem_spec import get_model_species_wrf
from emips import vertical_alloc
from collections import OrderedDict
import height
import merge
import transform
#Generate one(proj.py) or two(proj_2_file.py) emission files
import proj_2_file as proj

import os
import time

def run(run_config):
    """
    To CUACE model ready emission data files.

    :param run_config: (*RunConfigure*) The run configure.
    """

    time_start = time.time()

    mechanism_name = run_config.chemical_mechanism.name
    print('--------CHEMICAL MECHANISM: {}--------'.format(mechanism_name.upper()))

    # Set year and month
    year = run_config.emission_year
    month = run_config.emission_month

    # Set file path
    dir_in = run_config.run_output_dir
    dir_out = os.path.join(dir_in, 'WRFChem')
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)

    # Set model grid
    model_grid = run_config.spatial_model_grid

    # Set target grid
    target_proj = geolib.projinfo(proj='lcc', lon_0=103.5, lat_0=36.500008, lat_1=30.0, lat_2=60.0, a=6370000, b=6370000)
    target_grid = GridDesc(target_proj, x_orig=-2497499.597352108, x_cell=15000.0, x_num=334,
            y_orig=-2047499.8096037393, y_cell=15000.0, y_num=274)

    # Set path of the vertical allocate file
    z_file = run_config.vertical_prof_file

    # Set the number of z dimension
    vertical_pro = vertical_alloc.read_file(run_config.vertical_prof_file, run_config.emission_sectors[0].scc)
    zdim = len(vertical_pro.weights)

    # Set sectors that need to be processed
    # sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY,
    #         SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT]
    sectors = run_config.emission_sectors

    # Set global attributes
    gattrs = OrderedDict()
    #gattrs['Conventions'] = 'CF-1.6'
    gattrs['TITLE'] = 'Created using MeteoInfo, mechanism: {}'.format(mechanism_name.upper())
    gattrs['START_DATE'] = "{}-{:0>2d}-01_00:00:00".format(year, month)
    gattrs['WEST-EAST_GRID_DIMENSION'] = 335
    gattrs['SOUTH-NORTH_GRID_DIMENSION'] = 275
    gattrs['BOTTOM-TOP_GRID_DIMENSION'] = 8
    gattrs['DX'] = 15000.0
    gattrs['DY'] = 15000.0
    gattrs['WEST-EAST_PATCH_START_UNSTAG '] = 1
    gattrs['WEST-EAST_PATCH_END_UNSTAG'] = 334
    gattrs['WEST-EAST_PATCH_START_STAG'] = 1
    gattrs['WEST-EAST_PATCH_END_STAG'] = 335
    gattrs['SOUTH-NORTH_PATCH_START_UNSTAG'] = 1
    gattrs['SOUTH-NORTH_PATCH_END_UNSTAG'] = 274
    gattrs['SOUTH-NORTH_PATCH_START_STAG'] = 1
    gattrs['SOUTH-NORTH_PATCH_END_STAG'] = 275
    gattrs['BOTTOM-TOP_PATCH_START_UNSTAG'] = 1
    gattrs['BOTTOM-TOP_PATCH_END_UNSTAG'] = 7
    gattrs['BOTTOM-TOP_PATCH_START_STAG'] = 1
    gattrs['BOTTOM-TOP_PATCH_END_STAG'] = 8
    gattrs['CEN_LAT'] = 36.500008
    gattrs['CEN_LON'] = 103.5
    gattrs['TRUELAT1'] = 30.0
    gattrs['TRUELAT2'] = 60.0
    gattrs['MOAD_CEN_LAT'] = 36.500008
    gattrs['STAND_LON'] = 103.5
    gattrs['POLE_LAT'] = 90.0
    gattrs['POLE_LON'] = 0.0
    gattrs['GMT'] = 0.0
    gattrs['MAP_PROJ'] = 1
    gattrs['MAP_PROJ_CHAR'] = 'Lambert Conformal'
    gattrs['MMINLU'] = 'MODIFIED_IGBP_MODIS_NOAH'
    gattrs['NUM_LAND_CAT'] = 21
    gattrs['ISWATER'] = 17
    gattrs['ISLAKE'] = 21
    gattrs['ISICE'] = 15
    gattrs['ISURBAN'] = 13
    gattrs['ISOILWATER'] = 14

    ######set out species(gases and aerosol) and out species(aerosol)
    #################################################################################################
    ###------CB05,emiss_opt=15; RADM2,emiss_opt=3; SAPRC99,emiss_opt=13; MOZART,emiss_opt=10------###
    #################################################################################################
    out_species, out_species_aer = get_model_species_wrf(mechanism_name)

    # Run all scripts
    print('Allocate according to height...')
    height.run(year, month, dir_in, dir_out, model_grid, sectors, zdim, z_file)

    print('Merge data from different sectors...')
    merge.run(year, month, dir_in, dir_out, model_grid, sectors, zdim)

    print('Distribution of particulate matter and change unit...')
    transform.run(year, month, dir_in, dir_out, model_grid, out_species, out_species_aer, zdim)

    print('Conversion projection...')
    proj.run(year, month, dir_in, dir_out, model_grid, target_grid, out_species, out_species_aer, gattrs, mechanism_name, zdim)

    print('-------------------')
    print('---All finished!---')
    print('-------------------')

    time_end = time.time()
    time_count = (time_end - time_start) / 60
    print('Time: {:.2f}min'.format(time_count))