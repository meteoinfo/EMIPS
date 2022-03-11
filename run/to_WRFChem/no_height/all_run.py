'''
Merge files, convert pollutants and projection to meet WRF-Chem's input requirements(No height assignment).
'''

import time 
start_time = time.clock()

#Set current working directory
from inspect import getsourcefile
dir_run = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
if not dir_run in sys.path:
    sys.path.append(dir_run)

from emips.spatial_alloc import GridDesc
from collections import OrderedDict
import merge
import transform
#Generate one(proj.py) or two(proj_12.py) emission files
import proj

#set file path
year = 2017
month = 1
mechanism_name = 'radm2'
dir_inter = os.path.join(r'G:\test_data', mechanism_name, r'region_0.15\merge\{0:}\{0:}{1:>02d}'.format(year, month))

#set origin projection and grid
model_proj = geolib.projinfo()
model_grid = GridDesc(model_proj, x_orig=70., x_cell=0.15, x_num=502,
        y_orig=15., y_cell=0.15, y_num=330) 

#set target projection and grid
target_proj = geolib.projinfo(proj='lcc', lon_0=103.5, lat_0=36.500008, lat_1=30.0, lat_2=60.0, a=6370000, b=6370000)
target_grid = GridDesc(target_proj, x_orig=-2497499.597352108, x_cell=15000.0, x_num=334,
        y_orig=-2047499.8096037393, y_cell=15000.0, y_num=274)

#set sectors that need to be processed
sectors = ['agriculture', 'energy', 'industry', 'residential', 'transport', 'air', 'ships']

#set zdim of the output data
zdim = 3

#set out species(gases and aerosol) and out species(aerosol)
'''
#####CB05#####
out_species = ['E_ACET', 'E_PAR', 'E_ALK3', 'E_ALK4', 'E_ALK5', 'E_TOL', 'E_XYL', 'E_BALD', 
               'E_ALD2', 'E_CCOOH', 'E_CO', 'E_CRES', 'E_ETH', 'E_ETHA', 'E_GLY', 'E_FORM', 'E_HCOOH', 
               'E_IPROD', 'E_ISOP', 'E_MACR', 'E_MEK', 'E_MEOH', 'E_MEO2', 'E_ETOH', 'E_MGLY', 
               'E_NH3', 'E_HCL', 'E_NO', 'E_NO2', 'E_IOLE', 'E_OLE', 'E_PHEN', 'E_PROD2', 'E_ALDX', 
               'E_SO2', 'E_PSULF', 'E_TERP', 'E_PM25I', 'E_PM25J', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 
               'E_SO4I', 'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_SO4C', 'E_NO3C', 'E_ORGC', 'E_ECC', 'E_PM10']
out_species_aer = ['E_PM25I', 'E_PM25J', 'E_PM_10', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 
                       'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_SO4C', 'E_NO3C', 'E_ORGC', 'E_ECC']
'''

#####RADM2#####
out_species = ['E_ISO', 'E_SO2', 'E_NO', 'E_NO2', 'E_CO', 'E_CH4', 'E_ETH', 'E_HC3', 'E_HC5', 'E_HC8', 
                       'E_XYL', 'E_OL2', 'E_OLT', 'E_OLI', 'E_TOL', 'E_CSL', 'E_HCHO', 'E_ALD', 'E_KET', 'E_ORA2', 
                       'E_NH3', 'E_PM25I', 'E_PM25J', 'E_PM_10', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I',
                       'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_NAAJ', 'E_NAAI', 'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB',
                       'E_ORGJ_BB', 'E_HCL', 'E_CLI', 'E_CLJ', 'E_CH3CL']
out_species_aer = ['E_PM25I', 'E_PM25J', 'E_PM_10', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 
                       'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_NAAJ', 'E_NAAI', 'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB', 
                       'E_ORGJ_BB', 'E_CLI', 'E_CLJ']

'''
#####SAPRC99#####
out_species = ['E_SO2', 'E_C2H6', 'E_C3H8', 'E_C2H2', 'E_ALK3', 'E_ALK4', 'E_ALK5', 'E_ETHENE', 'E_C3H6', 
               'E_OLE1', 'E_OLE2', 'E_ARO1', 'E_ARO2', 'E_HCHO', 'E_CCHO', 'E_RCHO', 'E_ACET', 'E_MEK', 'E_ISOPRENE', 
               'E_TERP', 'E_SESQ', 'E_CO', 'E_NO', 'E_NO2', 'E_PHEN', 'E_CRES', 'E_MEOH', 'E_GLY', 'E_MGLY', 'E_BACL', 
               'E_ISOPROD', 'E_METHACRO', 'E_MVK', 'E_PROD2', 'E_CH4', 'E_BALD', 'E_HCOOH', 'E_CCO_OH', 'E_RCO_OH', 
               'E_NH3', 'E_PM25I', 'E_PM25J', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 'E_SO4J', 'E_NO3I', 'E_NO3J', 
               'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB', 'E_ORGJ_BB', 'E_PM10']
out_species_aer = ['E_PM25I', 'E_PM25J', 'E_PM_10', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 
                    'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB', 'E_ORGJ_BB']
'''
'''
#####MOZART#####
out_species = ['E_CO', 'E_NO', 'E_NO2', 'E_BIGALK', 'E_BIGENE', 'E_C2H4', 'E_C2H5OH', 'E_C2H6', 
               'E_C3H6', 'E_C3H8', 'E_CH2O', 'E_CH3CHO', 'E_CH3COCH3', 'E_CH3OH', 'E_MEK', 'E_SO2', 
               'E_TOLUENE', 'E_BENZENE', 'E_XYLENE', 'E_NH3', 'E_ISOP', 'E_APIN', 'E_PM25I', 'E_PM25J', 
               'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_NH4I', 
               'E_NH4J', 'E_NAI', 'E_NAJ', 'E_CLI', 'E_CLJ', 'E_CO_A', 'E_ORGI_A', 'E_ORGJ_A', 'E_CO_BB', 
               'E_ORGI_BB', 'E_ORGJ_BB', 'E_PM_10', 'E_C2H2', 'E_GLY', 'E_sulf', 'E_MACR', 'E_MGLY', 'E_MVK', 
               'E_HCOOH', 'E_HONO']
out_species_aer = ['E_PM25I', 'E_PM25J', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 'E_SO4J', 
                    'E_NO3I', 'E_NO3J', 'E_NH4I', 'E_NH4J', 'E_NAI', 'E_NAJ', 'E_CLI', 'E_CLJ', 
                    'E_CO_A', 'E_ORGI_A', 'E_ORGJ_A', 'E_CO_BB', 'E_ORGI_BB', 'E_ORGJ_BB', 'E_PM_10']
'''
#set global attributes
gattrs = OrderedDict()
#gattrs['Conventions'] = 'CF-1.6'
#gattrs['Tools'] = 'Created using MeteoInfo'
gattrs['TITLE'] = '  OUTPUT FROM *             PROGRAM:WRF-Chem V4.1.5 MODEL'
gattrs['START_DATE'] = "2017-01-01_00:00:00"
gattrs['WEST-EAST_GRID_DIMENSION'] = 335
gattrs['SOUTH-NORTH_GRID_DIMENSION'] = 275
gattrs['BOTTOM-TOP_GRID_DIMENSION'] = 28
gattrs['DX'] = 15000.0
gattrs['DY'] = 15000.0
'''
gattrs['AERCU_OPT'] = 0
gattrs['AERCU_FCT'] = 1.0
gattrs['IDEAL_CASE'] = 0
gattrs['DIFF_6TH_SLOPEOPT'] = 0
gattrs['AUTO_LEVELS_OPT'] = 2
gattrs['DIFF_6TH_THRESH'] = 0.1
gattrs['DZBOT'] = 50.0
gattrs['DZSTRETCH_S'] = 1.3
gattrs['DZSTRETCH_U'] = 1.1
gattrs['GRIDTYPE'] = "C"
gattrs['DIFF_OPT'] = 1
gattrs['KM_OPT'] = 4
gattrs['DAMP_OPT'] = 3
gattrs['DAMPCOEF'] = 0.2
gattrs['KHDIF'] = 0.0
gattrs['KVDIF'] = 0.0
gattrs['MP_PHYSICS'] = 2
gattrs['RA_LW_PHYSICS'] = 4
gattrs['RA_SW_PHYSICS'] = 4
gattrs['SF_SFCLAY_PHYSICS'] = 2
gattrs['SF_SURFACE_PHYSICS'] = 2
gattrs['BL_PBL_PHYSICS'] = 2
gattrs['CU_PHYSICS'] = 10
gattrs['SF_LAKE_PHYSICS'] = 0
gattrs['SURFACE_INPUT_SOURCE'] = 3
gattrs['SST_UPDATE'] = 0
gattrs['GRID_FDDA'] = 1
gattrs['GFDDA_INTERVAL_M'] = 0
gattrs['GFDDA_END_H'] = 0
gattrs['GRID_SFDDA'] = 0
gattrs['SGFDDA_INTERVAL_M'] = 0
gattrs['SGFDDA_END_H'] = 0
gattrs['HYPSOMETRIC_OPT'] = 2
gattrs['USE_THETA_M'] = 1
gattrs['GWD_OPT'] = 1
gattrs['SF_URBAN_PHYSICS'] = 0
gattrs['SF_SURFACE_MOSAIC'] = 0
gattrs['SF_OCEAN_PHYSICS'] = 0
'''
gattrs['WEST-EAST_PATCH_START_UNSTAG '] = 1
gattrs['WEST-EAST_PATCH_END_UNSTAG'] = 334
gattrs['WEST-EAST_PATCH_START_STAG'] = 1
gattrs['WEST-EAST_PATCH_END_STAG'] = 335
gattrs['SOUTH-NORTH_PATCH_START_UNSTAG'] = 1
gattrs['SOUTH-NORTH_PATCH_END_UNSTAG'] = 274
gattrs['SOUTH-NORTH_PATCH_START_STAG'] = 1
gattrs['SOUTH-NORTH_PATCH_END_STAG'] = 275
gattrs['BOTTOM-TOP_PATCH_START_UNSTAG'] = 1
gattrs['BOTTOM-TOP_PATCH_END_UNSTAG'] = 27
gattrs['BOTTOM-TOP_PATCH_START_STAG'] = 1
gattrs['BOTTOM-TOP_PATCH_END_STAG'] = 28
gattrs['GRID_ID'] = 1
gattrs['PARENT_ID'] = 1
gattrs['I_PARENT_START'] = 1
gattrs['J_PARENT_START'] = 1
gattrs['PARENT_GRID_RATIO'] = 1
gattrs['DT'] = 90.0
gattrs['CEN_LAT'] = 36.500008
gattrs['CEN_LON'] = 103.5
gattrs['TRUELAT1'] = 30.0
gattrs['TRUELAT2'] = 60.0
gattrs['MOAD_CEN_LAT'] = 36.500008
gattrs['STAND_LON'] = 103.5
gattrs['POLE_LAT'] = 90.0
gattrs['POLE_LON'] = 0.0
gattrs['GMT'] = 0.0
gattrs['JULYR'] = 2016
gattrs['JULDAY'] = 365
gattrs['MAP_PROJ'] = 1
gattrs['MAP_PROJ_CHAR'] = 'Lambert Conformal'
gattrs['MMINLU'] = 'MODIFIED_IGBP_MODIS_NOAH'
'''
gattrs['NUM_LAND_CAT'] = 21
gattrs['ISWATER'] = 17
gattrs['ISLAKE'] = 21
gattrs['ISICE'] = 15
gattrs['ISURBAN'] = 13
gattrs['ISOILWATER'] = 14
gattrs['HYBRID_OPT'] = 2
gattrs['ETAC'] = 0.15    
'''
#run all scripts
print('Merge sector data...')
#merge.run_merge(year, month, dir_inter, model_grid, sectors)
print('Distribution of particulate matter and change unit...')
#transform.run_transform(year, month, dir_inter, model_grid, out_species, out_species_aer)
print('Conversion projection...')
proj.run_proj(year, month, dir_inter, model_grid, target_grid, out_species, out_species_aer, gattrs, zdim)

print('-------------------')
print('---All finished!---')
print('-------------------')

end_time = time.clock()
time = (end_time - start_time)/60
print('Time: {}'.format(time))