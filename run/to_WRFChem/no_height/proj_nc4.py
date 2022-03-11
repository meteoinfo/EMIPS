from emips.spatial_alloc import GridDesc, transform
from collections import OrderedDict
from mipylib import dataset
import mipylib.numeric as np

out_species = ['E_ISO', 'E_SO2', 'E_NO', 'E_NO2', 'E_CO', 'E_CH4', 'E_ETH', 'E_HC3', 'E_HC5', 'E_HC8', 
                       'E_XYL', 'E_OL2', 'E_OLT', 'E_OLI', 'E_TOL', 'E_CSL', 'E_HCHO', 'E_ALD', 'E_KET', 'E_ORA2', 
                       'E_NH3', 'E_PM25I', 'E_PM25J', 'E_PM_10', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I',
                       'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_NAAJ', 'E_NAAI', 'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB',
                       'E_ORGJ_BB', 'E_HCL', 'E_CLI', 'E_CLJ', 'E_CH3CL']
out_species_unit = ['E_PM25I', 'E_PM25J', 'E_PM_10', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 
                       'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_NAAJ', 'E_NAAI', 'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB', 
                       'E_ORGJ_BB', 'E_CLI', 'E_CLJ']

def run_proj(year, month, dir_inter, model_grid, target_grid):
    print('Add input file...')
    fn_in = dir_inter + '\emis_{}_{}_hour_transform.nc'.format(year, month)
    print(fn_in)
    f_in = dataset.addfile(fn_in)
    #set dimension 
    tdim = np.dimension(np.arange(24), 'Time')
    ydim = np.dimension(target_grid.y_coord, 'south_north', 'Y')
    xdim = np.dimension(target_grid.x_coord, 'west_east', 'X')
    zdim = np.dimension(np.arange(3), 'emissions_zdim')
    sdim = np.dimension(np.arange(19), 'DateStrLen')
    dims = [tdim, zdim, ydim, xdim]
    all_dims = [tdim, sdim, xdim, ydim, zdim]
    
    #set global attributes
    gattrs = OrderedDict()
    #gattrs['Conventions'] = 'CF-1.6'
    #gattrs['Tools'] = 'Created using MeteoInfo'
    gattrs['TITLE'] = ' OUTPUT FROM *             PROGRAM:WRF-Chem V4.1.5 MODEL'
    gattrs['START_DATE'] = "2017-01-01_00:00:00"
    gattrs['WEST-EAST_GRID_DIMENSION'] = 335
    gattrs['SOUTH-NORTH_GRID_DIMENSION'] = 275
    gattrs['BOTTOM-TOP_GRID_DIMENSION'] = 28
    gattrs['DX'] = 15000.0
    gattrs['DY'] = 15000.0
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
    gattrs['PARENT_ID'] = 0
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
    gattrs['NUM_LAND_CAT'] = 21
    gattrs['ISWATER'] = 17
    gattrs['ISLAKE'] = 21
    gattrs['ISICE'] = 15
    gattrs['ISURBAN'] = 13
    gattrs['ISOILWATER'] = 14
    gattrs['HYBRID_OPT'] = 2
    gattrs['ETAC'] = 0.15                                                                                             

    fn_out = dir_inter + '\emis_{}_{}_hour_proj_nc4.nc'.format(year, month)
    #fn_out = dir_inter + '\emis_{}_{}_hour_proj_chunk.nc'.format(year, month)
    
    #set variables
    dimvars = []
    
    dimvar = dataset.DimVariable()
    dimvar.name = 'Times'
    dimvar.dtype = np.dtype.char
    dimvar.dims = [tdim, sdim]
    dimvar.addattr('_ChunkSizes', np.array([1, 19], dtype=np.dtype.uint))
    #dimvar.addattr('_ChunkSizes', [1, 19])
    dimvars.append(dimvar)
    
    for out_specie in out_species:
        dimvar = dataset.DimVariable()
        dimvar.name = out_specie
        dimvar.dtype = np.dtype.float
        dimvar.dims = dims
        dimvar.addattr('FieldType', 104)
        dimvar.addattr('MemoryOrder', "XYZ")
        dimvar.addattr('description', "EMISSION_{}".format(out_specie[2:]))
        if out_specie in out_species_unit:
            #g/m2/s to ug/m^3 m/s
            dimvar.addattr('units', 'ug/m3 m/s')
        else:
            #mole/m2/s to mol/km^2/hr
            dimvar.addattr('units', 'mol km^-2 hr^-1')
        dimvar.addattr('stagger', "")
        dimvar.addattr('coordinates', "XLONG XLAT XTIME")
        dimvar.addattr('_ChunkSizes', array([1, 3, 137, 167], dtype=np.dtype.uint))
        #dimvar.addattr('_ChunkSizes', [1, 3, 137, 167])
        dimvars.append(dimvar)
    
    print('Create output data file...')
    print(fn_out)
    ncfile = dataset.addfile(fn_out, 'c', version='netcdf4', largefile=True)
    #ncfile = dataset.addfile(fn_out, 'c', largefile=True)
    print('Define dimensions, global attributes and variables...')
    ncfile.nc_define(all_dims, gattrs, dimvars, write_dimvars=False) 
       
    #Times
    print('Write Times variable...')
    s_out = []
    for i in range(24):
        s = '{}-{:0>2d}-01_{:0>2d}:00:00'.format(year, month, i)
        s_out.append(s)
    s_out = np.array(s_out, dtype=np.dtype.char)
    ncfile.write('Times', s_out)
    
    print('Write variable data except times...')
    for out_specie in out_species:
        if out_specie in f_in.varnames():
            print(out_specie)
            data = f_in[out_specie][:]
            #Conversion
            data = transform(data, model_grid, target_grid)
            #Set the fourth dimension 
            data = data.reshape(24, 1, 274, 334)
            #Set default values
            data[data==np.nan] = 0
            ncfile.write(out_specie, data)
    ncfile.close()
    print('Conversion projection finished!')
if __name__ == '__main__':
    #set target projection
    f_example = addfile(r'D:\chen\Emission_Inventory\model_data\radm2\wrfchemi_d01_radm2_201701')
    #set parameter 
    year = 2017
    month = 1
    dir_inter = r'D:\chen\MEIC_data\radm2_wrfchem_test\{}{:>02d}'.format(year, month)
    model_grid = GridDesc(geolib.projinfo(), x_orig=70., x_cell=0.15, x_num=502,
        y_orig=15., y_cell=0.15, y_num=330)
    target_grid = GridDesc(f_example.proj, x_orig=-2505000.0, x_cell=15000.0, x_num=334,
        y_orig=-2055000.0, y_cell=15000.0, y_num=274)
    #run
    run_proj(year, month, dir_inter, model_grid, target_grid)
    

