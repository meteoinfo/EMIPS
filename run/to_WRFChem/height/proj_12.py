from emips.spatial_alloc import GridDesc, transform
from collections import OrderedDict
from mipylib import dataset
import mipylib.numeric as np


def run_proj(year, month, dir_inter, model_grid, target_grid, out_species, out_species_aer, global_attributes, z):
    """
    Write Times variable, add global attributes, convert data's projection.
	io_style_emissions = 1

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
    tdim = np.dimension(np.arange(12), 'Time')
    ydim = np.dimension(target_grid.y_coord, 'south_north', 'Y')
    xdim = np.dimension(target_grid.x_coord, 'west_east', 'X')
    zdim = np.dimension(np.arange(z), 'emissions_zdim')
    sdim = np.dimension(np.arange(19), 'DateStrLen')
    dims = [tdim, zdim, ydim, xdim]
    all_dims = [tdim, sdim, xdim, ydim, zdim]
    
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
    for num in [0, 12]:   
        fn_out = dir_inter + '\wrfchemi_{:0>2d}z_d01'.format(num)

        print('Create output data file...')
        print(fn_out)
        ncfile = dataset.addfile(fn_out, 'c', largefile=True)
        print('Define dimensions, global attributes and variables...')
        ncfile.nc_define(all_dims, global_attributes, dimvars, write_dimvars=False)
        
        #Times
        print('Write Times variable...')
        s_out = []
        for i in range(num, num+12):
            s = '{}-{:0>2d}-01_{:0>2d}:00:00'.format(year, month, i)
            s_out.append(s)
        s_out = np.array(s_out, dtype=np.dtype.char)
        ncfile.write('Times', s_out)
        
        print('Write variable data except times...')
        for out_specie in out_species:
            data = np.zeros((tdim.length, zdim.length, ydim.length, xdim.length))
            if out_specie in f_in.varnames():
                print(out_specie)
                dd = f_in[out_specie][num:num+12]
                #Conversion
                dd = transform(dd, model_grid, target_grid)
                #Set the fourth dimension 
                #dd = dd.reshape(12, 1, ydim.length, xdim.length)
                #Set default values
                dd[dd==np.nan] = 0
            else:
                print('{} no data!'.format(out_specie))
                dd = f_in['E_ISO'][num:num+12]
                dd[:, :, :, :] = 0
                dd = transform(dd, model_grid, target_grid)
                #Set the fourth dimension 
                #dd = dd.reshape(12, 1, ydim.length, xdim.length)
                #Set default values
                dd[dd==np.nan] = 0
            data[:, :, :, :] = dd
            ncfile.write(out_specie, data)
        ncfile.close()
    print('Convert projection finished and split into two files finished!')
    
if __name__ == '__main__':
    #set target projection
    f_example = addfile(r'Z:\chen\Emission_Inventory\model_data\radm2\wrfchemi_d01_radm2_201701')
    #set parameter 
    year = 2017
    month = 1
    dir_inter = r'E:\emips_data\merge\region_0.1\2017_tw\{}{:>02d}'.format(year, month)
    model_grid = GridDesc(geolib.projinfo(), x_orig=70., x_cell=0.1, x_num=751,
        y_orig=15., y_cell=0.1, y_num=501)
    target_grid = GridDesc(f_example.proj, x_orig=-2497499.597352108, x_cell=15000.0, x_num=334,
        y_orig=-2047499.8096037393, y_cell=15000.0, y_num=274)

    z = 8
    #run
    run_proj(year, month, dir_inter, model_grid, target_grid, z)
    

