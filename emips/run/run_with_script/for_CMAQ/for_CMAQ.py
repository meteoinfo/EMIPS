"""
# Author: Wencong Chen
# Date: 2023-06-21
# Purpose: Convert model-ready emission file to meet CMAQ's input requirements.
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
from emips.chem_spec import get_model_species_CMAQ
from collections import OrderedDict
import datetime
import height
import merge
import transform
import proj

#Choose Chemical mechanism
mechanism_name = 'cb05'
print('--------CHEMICAL MECHANISM: {}--------'.format(mechanism_name.upper()))

#Set year and month
year = 2019
month = 1

#Set input&output file path
dir_inter = os.path.join(r'G:\CMAQ', mechanism_name, r'merge\{0:}\{0:}{1:>02d}'.format(year, month))

#Set original grid
original_proj = geolib.projinfo()
original_grid = GridDesc(original_proj, x_orig=64., x_cell=0.25, x_num=324,
    y_orig=15., y_cell=0.25, y_num=180)
    
#Set target grid
ncols = 164             #the number of x dimension
nrows = 97              #the number of y dimension
nlays = 7               #the number of z dimension
xcell = 36000.0         #Grid spacing in x dimensions
ycell = 36000.0         #Grid spacing in y dimensions
proj_name = 'lcc'       #Name of the projection ('lcc' is Lambert Conformal Conic projection)
xcent = 110.0           #Longitude of projection center
ycent = 34.0            #Latitude of projection center
p_alp = 25.0            #First standard parallel
p_bet = 40.0            #Second standard parallel
p_gam = 110.0
radius = 6370000.0      #Radius of the sphere(unit: meter)

if ncols % 2 == 0:
    xorig = (ncols-2) / 2.0 * xcell + xcell / 2.0
else:
    xorig = (ncols-1) / 2.0 * xcell
if nrows % 2 == 0:
    yorig = (nrows-2) / 2.0 * ycell + ycell / 2.0
else:
    yorig = (nrows-1) / 2.0 * ycell
target_proj = geolib.projinfo(proj=proj_name, lon_0=xcent, lat_0=ycent, lat_1=p_alp, lat_2=p_bet, a=radius, b=radius)
target_grid = GridDesc(target_proj, x_orig=-xorig, x_cell=xcell, x_num=ncols,
        y_orig=-yorig, y_cell=ycell, y_num=nrows)

#Set path of the vertical allocate file
vert_prof_file = os.path.join(ge_data_dir, 'height.txt')

#Set sectors that need to be processed
sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY,
        SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT] 

#Acquisition of model species (gases and aerosol) and aerosol names based on chemical mechanisms
out_species, out_species_aer = get_model_species_CMAQ(mechanism_name)
varlist = ''
for i in out_species:
    varlist = varlist + '{:<16s}'.format(i)

#Set global attributes
gattrs = OrderedDict()
#gattrs['Conventions'] = 'CF-1.6'
gattrs['TITLE'] = "Created using MeteoInfo, mechanism: {}".format(mechanism_name.upper())
gattrs['IOAPI_VERSION'] = "{:<80s}".format('$Id: @(#) ioapi library version 3.1 $')
gattrs['EXEC_ID'] = "{:<80s}".format('????????????????')
gattrs['FTYPE'] = 1
gattrs['CDATE'] = datetime.date(year=year, month=month, day=1).strftime("%Y%j")  #test
gattrs['CTIME'] = 81255                                                          #test
gattrs['WDATE'] = datetime.date(year=year, month=month, day=1).strftime("%Y%j")  #test
gattrs['WTIME'] = 81255                                                          #test
gattrs['SDATE'] = datetime.date(year=year, month=month, day=1).strftime("%Y%j")
gattrs['STIME'] = 0
gattrs['TSTEP'] = 10000
gattrs['NTHIK'] = 1
gattrs['NCOLS'] = ncols
gattrs['NROWS'] = nrows
gattrs['NLAYS'] = nlays
gattrs['NVARS'] = len(out_species)
gattrs['GDTYP'] = 2
gattrs['P_ALP'] = p_alp
gattrs['P_BET'] = p_bet
gattrs['P_GAM'] = p_gam
gattrs['XCENT'] = xcent
gattrs['YCENT'] = ycent
gattrs['XORIG'] = -xorig
gattrs['YORIG'] = -yorig
gattrs['XCELL'] = xcell
gattrs['YCELL'] = ycell
gattrs['VGTYP'] = 2                #test
gattrs['VGTOP'] = 10000.0
gattrs['VGLVLS'] = 1.0, 0.995, 0.988, 0.98, 0.97, 0.956, 0.938, 0.893, 0.839, 0.777, 0.702, 0.582, 0.4, 0.2, 0.0
gattrs['GDNAM'] = "{:<16s}".format('M_36_08CHINA')
gattrs['UPNAM'] = ""
gattrs['VAR-LIST'] = varlist
gattrs['FILEDESC'] = ""
gattrs['HISTORY'] = ""

#Run all scripts
print('Allocate according to height...')
height.run(year, month, dir_inter, original_grid, sectors, nlays, vert_prof_file)
print('Merge data from different sectors...')
merge.run(year, month, dir_inter, original_grid, sectors, nlays)
print('Distribution of particulate matter and change unit...')
transform.run(year, month, dir_inter, original_grid, out_species, out_species_aer, nlays)
print('Conversion projection...')
proj.run(year, month, dir_inter, original_grid, target_grid, out_species, out_species_aer, gattrs, mechanism_name, nlays)
print('-----------------------------')
print('--------All finished!--------')
print('-----------------------------')

#Calculate running time
end_time = time.clock()
time = (end_time - start_time) / 60.0
print('Time: {:.2f}min'.format(time))