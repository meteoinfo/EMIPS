from emips.spatial_alloc import GridDesc, transform
from collections import OrderedDict
from mipylib import dataset
import mipylib.numeric as np


def run_proj(year, month, dir_inter, model_grid, target_grid, out_species, out_species_aer, global_attributes, z):
    """
    Write Times variable, add global attributes, convert data's projection.
	io_style_emissions = 2

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param target_grid: (*GridDesc*) Target data grid describe.
    :param out_species: (*list*) The name of the output species(gases and aerosol).
    :param out_species_aer: (*list*) The name of the output species(aerosol).
    :param global_attributes: (*OrderedDict*) The global attributes of the output file.
    :param z: (*int*) The zdim of the output data.
    """
    print('Add input file...')
    fn_in = dir_inter + '\emis_{}_{}_hour_transform.nc'.format(year, month)
    print(fn_in)
    f_in = dataset.addfile(fn_in)
    #set dimension 
    tdim = np.dimension(np.arange(24), 'Time')
    ydim = np.dimension(target_grid.y_coord, 'south_north', 'Y')
    xdim = np.dimension(target_grid.x_coord, 'west_east', 'X')
    zdim = np.dimension(np.arange(z), 'emissions_zdim')
    sdim = np.dimension(np.arange(19), 'DateStrLen')
    dims = [tdim, zdim, ydim, xdim]
    all_dims = [tdim, sdim, xdim, ydim, zdim]

    fn_out = dir_inter + '\wrfchemi_d01_{}-{:0>2d}'.format(year, month)
    
    #set variables
    dimvars = []
    
    dimvar = dataset.DimVariable()
    dimvar.name = 'Times'
    dimvar.dtype = np.dtype.char
    dimvar.dims = [tdim, sdim]
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
        if out_specie in out_species_aer:
            #g/m2/s to ug/m^3 m/s
            dimvar.addattr('units', 'ug/m3 m/s')
        else:
            #mole/m2/s to mol/km^2/hr
            dimvar.addattr('units', 'mol km^-2 hr^-1')
        dimvar.addattr('stagger', "")
        dimvar.addattr('coordinates', "XLONG XLAT XTIME")
        #dimvar.addattr('_ChunkSizes', [1, 3, 137, 167])
        dimvars.append(dimvar)
    
    print('Create output data file...')
    print(fn_out)
    ncfile = dataset.addfile(fn_out, 'c', largefile=True)
    print('Define dimensions, global attributes and variables...')
    ncfile.nc_define(all_dims, global_attributes, dimvars, write_dimvars=False)
       
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
        data = np.zeros((tdim.length, zdim.length, ydim.length, xdim.length))
        if out_specie in f_in.varnames():
            print(out_specie)
            dd = f_in[out_specie][:]
            #Conversion proj
            dd = transform(dd, model_grid, target_grid)
            #Set default values
            dd[dd==np.nan] = 0
            data[:, :, :, :] = dd
            ##########test############
            #data[:, 1:8, :, :] = 0  
            ##########test############
            ncfile.write(out_specie, data)
    f_in.close()
    ncfile.close()
    print('Convert projection finished!')

    
if __name__ == '__main__':
    #set target projection
    #f_example = addfile(r'Z:\chen\Emission_Inventory\model_data\saprc99\wrfchemi_d01_saprc99_201701')
    proj = geolib.projinfo(proj='lcc', lon_0=103.5, lat_0=36.500008, lat_1=30.0, lat_2=60.0, a=6370000, b=6370000)
    #set parameter 
    year = 2017
    month = 1
    dir_inter = r'G:\test_data\saprc99\region_0.15\merge\{0:}\{0:}{1:>02d}'.format(year, month)
    model_grid = GridDesc(geolib.projinfo(), x_orig=70., x_cell=0.15, x_num=502,
        y_orig=15., y_cell=0.15, y_num=330) 
    target_grid = GridDesc(proj, x_orig=-2505000.0, x_cell=15000.0, x_num=334,
        y_orig=-2055000.0, y_cell=15000.0, y_num=274)
    z = 8
    out_species = ['E_SO2', 'E_C2H6', 'E_C3H8', 'E_C2H2', 'E_ALK3', 'E_ALK4', 'E_ALK5', 'E_ETHENE', 'E_C3H6', 
               'E_OLE1', 'E_OLE2', 'E_ARO1', 'E_ARO2', 'E_HCHO', 'E_CCHO', 'E_RCHO', 'E_ACET', 'E_MEK', 'E_ISOPRENE', 
               'E_TERP', 'E_SESQ', 'E_CO', 'E_NO', 'E_NO2', 'E_PHEN']
    out_species_unit = ['E_PM25I', 'E_PM25J', 'E_PM_10', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 
                    'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB', 'E_ORGJ_BB']
    #run
    run_proj(year, month, dir_inter, model_grid, target_grid, out_species, out_species_unit, z)
    

