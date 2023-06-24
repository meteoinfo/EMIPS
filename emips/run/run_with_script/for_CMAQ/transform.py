from emips.spatial_alloc import GridDesc
from collections import OrderedDict
from mipylib import dataset
import mipylib.numeric as np

def run(year, month, dir_inter, model_grid, out_species, out_species_aer, nlays):
    """
    Change unit and match variable name.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param out_species: (*list*) The name of the output species (gases and aerosol).
    :param out_species_aer: (*list*) The name of the output species (aerosol).
    :param nlays: (*int*) The z-dimension of the output data.
    """
    print('Add input file...')
    fn_in = dir_inter + '\emis_{}_{}_hour.nc'.format(year, month)
    f_in = dataset.addfile(fn_in)
    
    #Set dimension
    print('Define dimensions and global attributes...')
    tdim = np.dimension(np.arange(24), 'TSTEP')
    zdim = np.dimension(np.arange(nlays), 'LAY')
    ydim = np.dimension(model_grid.y_coord, 'ROW', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'COL', 'X')
    dims = [tdim, zdim, ydim, xdim]
    gattrs = OrderedDict()
    gattrs['Conventions'] = 'CF-1.6'
    gattrs['Tools'] = 'Created using MeteoInfo'
    
    #Set the definition of the output variable and ncfile
    fn_out = dir_inter + '\emis_{}_{}_hour_transform.nc'.format(year, month)
    print('Define variables and output file...')
    dimvars = []
    for out_specie in out_species:
        dimvar = dataset.DimVariable()
        dimvar.name = out_specie
        dimvar.dtype = np.dtype.float
        dimvar.dims = dims
        dimvar.addattr('long_name', "{:<16s}".format(out_specie))
        if out_specie in out_species_aer:
            #g/m2/s to g/grid/s
            dimvar.addattr('units', "{:<16s}".format('g/s'))
        else:
            #mole/m2/s to moles/grid/s
            dimvar.addattr('units', "{:<16s}".format('moles/s'))
        dimvar.addattr('var_desc', "{:<80s}".format("Hourly emission"))
        dimvars.append(dimvar)
    print('Create output data file:{}'.format(fn_out))
    ncfile = dataset.addfile(fn_out, 'c', largefile=True)
    ncfile.nc_define(dims, gattrs, dimvars)    

    #calculate grid areas (meter)
    grid_areas = np.zeros((tdim.length, zdim.length, ydim.length, xdim.length))
    for i in range(tdim.length):
        for j in range(zdim.length):
            grid_areas[i, j, :, :] = model_grid.grid_areas()
    
    #add data to ncfile
    print('Process data and write to file...')
    for name in out_species:
        data = np.zeros((tdim.length, zdim.length, ydim.length, xdim.length))
        sname = name
        print(sname)
        if sname in f_in.varnames:
            data = f_in[sname][:, :, :, :]
#            data = data * 1e6
            data = data * grid_areas
            ncfile.write(name, data)
        elif sname == 'UNR':
            data = f_in['NR'][:, :, :]
            data = data * grid_areas
            ncfile.write(name, data)
        elif sname == 'PMOTHR':
            data = f_in['PMFINE'][:, :, :]
            data = data * grid_areas
            ncfile.write(name, data)
        #####test#####
        elif sname == 'POC':
            data = f_in['POA'][:, :, :]
            data = data * grid_areas
            ncfile.write(name, data)
        #####test#####
        else:
            ncfile.write(name, data)
    f_in.close()
    ncfile.close()      
    print('Distribution of particulate matter and change unit finised!')
