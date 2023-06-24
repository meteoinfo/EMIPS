"""
# Author: Wencong Chen
# Date: 2022-08-04
# Purpose: Convert model-ready emission file to meet WRF-Chem's input requirements.
           (height allocation, merge files of different sectors, convert pollutants and projection)
"""

import time 
start_time = time.clock()
#Set current working directory
from inspect import getsourcefile
dir_run = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
if not dir_run in sys.path:
    sys.path.append(dir_run)

import os
from emips.spatial_alloc import GridDesc
from emips import ge_data_dir
from emips.utils import SectorEnum
from emips.chem_spec import get_model_species_WRFChem
from collections import OrderedDict
import height
import merge
import transform

#Generate one(proj.py) or two(proj_2_file.py) emission files
import proj_2_file as proj

#Choose Chemical mechanism
mechanism_name = 'radm2'
print('--------CHEMICAL MECHANISM: {}--------'.format(mechanism_name.upper()))

#Set year and month
year = 2017
month = 1

#Set input&output file path
dir_inter = os.path.join(r'G:\test', mechanism_name, r'merge\{0:}\{0:}{1:>02d}'.format(year, month))

#Set original grid
original_proj = geolib.projinfo()
original_grid = GridDesc(original_proj, x_orig=64., x_cell=0.25, x_num=324,
    y_orig=15., y_cell=0.25, y_num=180)
    
#set target grid
e_we = 335              #the number of x dimension
e_sn = 275              #the number of y dimension
zdim = 7                #the number of z dimension
dx = 15000.0            #Grid spacing in x dimensions
dy = 15000.0            #Grid spacing in y dimensions
proj_name = 'lcc'       #Name of the projection ('lcc' is Lambert Conformal Conic projection)
ref_lat = 36.500008     #Latitude of projection center
ref_lon = 103.5         #Longitude of projection center
truelat1 = 30.0         #First standard parallel
truelat2 = 60.0         #Second standard parallel
stand_lon = 103.5
radius = 6370000.0      #Radius of the sphere(unit: meter)

if (e_we-1) % 2 == 0:
    xmin = (e_we-3) / 2.0 * dx + dx / 2.0
else:
    xmin = (e_we-2) / 2.0 * dx
if (e_sn-1) % 2 == 0:
    ymin = (e_sn-3) / 2.0 * dy + dy / 2.0
else:
    ymin = (e_sn-2) / 2.0 * dy 
target_proj = geolib.projinfo(proj=proj_name, lon_0=ref_lon, lat_0=ref_lat, lat_1=truelat1, lat_2=truelat2, a=radius, b=radius)
target_grid = GridDesc(target_proj, x_orig=-xmin, x_cell=dx, x_num=e_we-1,
        y_orig=-ymin, y_cell=dy, y_num=e_sn-1)

#Set path of the vertical allocate file
vert_prof_file = os.path.join(ge_data_dir, 'height.txt')

#Set sectors that need to be processed
sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY,
        SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT] 

#set global attributes
gattrs = OrderedDict()
#gattrs['Conventions'] = 'CF-1.6'
gattrs['TITLE'] = 'Created using MeteoInfo, mechanism: {}'.format(mechanism_name.upper())
gattrs['START_DATE'] = "{}-{:0>2d}-01_00:00:00".format(year, month)
gattrs['WEST-EAST_GRID_DIMENSION'] = e_we
gattrs['SOUTH-NORTH_GRID_DIMENSION'] = e_sn
gattrs['BOTTOM-TOP_GRID_DIMENSION'] = zdim + 1
gattrs['DX'] = dx
gattrs['DY'] = dy
gattrs['WEST-EAST_PATCH_START_UNSTAG'] = 1
gattrs['WEST-EAST_PATCH_END_UNSTAG'] = e_we - 1
gattrs['WEST-EAST_PATCH_START_STAG'] = 1
gattrs['WEST-EAST_PATCH_END_STAG'] = e_we
gattrs['SOUTH-NORTH_PATCH_START_UNSTAG'] = 1
gattrs['SOUTH-NORTH_PATCH_END_UNSTAG'] = e_sn - 1
gattrs['SOUTH-NORTH_PATCH_START_STAG'] = 1
gattrs['SOUTH-NORTH_PATCH_END_STAG'] = e_sn
gattrs['BOTTOM-TOP_PATCH_START_UNSTAG'] = 1
gattrs['BOTTOM-TOP_PATCH_END_UNSTAG'] = zdim
gattrs['BOTTOM-TOP_PATCH_START_STAG'] = 1
gattrs['BOTTOM-TOP_PATCH_END_STAG'] = zdim + 1
gattrs['CEN_LAT'] = ref_lat
gattrs['CEN_LON'] = ref_lon
gattrs['TRUELAT1'] = truelat1
gattrs['TRUELAT2'] = truelat2
gattrs['MOAD_CEN_LAT'] = ref_lat
gattrs['STAND_LON'] = stand_lon
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

##Acquisition of model species (gases and aerosol) and aerosol names based on chemical mechanisms
###------CB05,emiss_opt=15; RADM2,emiss_opt=3; SAPRC99,emiss_opt=13; MOZART,emiss_opt=10------###
out_species, out_species_aer = get_model_species_WRFChem(mechanism_name)

#Run all scripts
print('Allocate according to height...')
height.run(year, month, dir_inter, original_grid, sectors, zdim, vert_prof_file)
print('Merge data from different sectors...')
merge.run(year, month, dir_inter, original_grid, sectors, zdim)
print('Distribution of particulate matter and change unit...')
transform.run(year, month, dir_inter, original_grid, out_species, out_species_aer, zdim)
print('Conversion projection...')
proj.run(year, month, dir_inter, original_grid, target_grid, out_species, out_species_aer, gattrs, mechanism_name, zdim)
print('-----------------------------')
print('--------All finished!--------')
print('-----------------------------')

#Calculate running time
end_time = time.clock()
time = (end_time - start_time) / 60.0
print('Time: {:.2f}min'.format(time))