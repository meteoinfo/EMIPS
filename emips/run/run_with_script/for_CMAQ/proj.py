from emips.spatial_alloc import GridDesc, transform
from collections import OrderedDict
from mipylib import dataset
import mipylib.numeric as np
import datetime

def run(year, month, dir_inter, model_grid, target_grid, out_species, out_species_aer, global_attributes, mechanism_name, nlays):
    """
    Write Times variable, add global attributes, convert data's projection.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param target_grid: (*GridDesc*) Target data grid describe.
    :param out_species: (*list*) The name of the output species (gases and aerosol).
    :param out_species_aer: (*list*) The name of the output species (aerosol).
    :param global_attributes: (*OrderedDict*) The global attributes of the output file.
    :param mechanism_name: (*string*) The name of the chemical mechanism.
    :param nlays: (*int*) The z-dimension of the output data.
    """
    print('Add input file...')
    fn_in = dir_inter + '\emis_{}_{}_hour_transform.nc'.format(year, month)
    print(fn_in)
    f_in = dataset.addfile(fn_in)
    
    #set dimension 
    tdim = np.dimension(np.arange(25), 'TSTEP')
    ddim = np.dimension(np.arange(2), 'DATE-TIME')
    ydim = np.dimension(target_grid.y_coord, 'ROW', 'Y')
    xdim = np.dimension(target_grid.x_coord, 'COL', 'X')
    zdim = np.dimension(np.arange(nlays), 'LAY')
    vdim = np.dimension(np.arange(len(out_species)), 'VAR')
    vardims = [tdim, zdim, ydim, xdim]
    all_dims = [tdim, ddim, zdim, vdim, ydim, xdim]
    
    #Set variables
    dimvars = []
    dimvar = dataset.DimVariable()
    dimvar.name = 'TFLAG'
    dimvar.dtype = np.dtype.int
    dimvar.dims = [tdim, vdim, ddim]
    dimvar.addattr('units', '<YYYYDDD,HHMMSS>')
    dimvar.addattr('long_name', '{:<16s}'.format('TFLAG'))
    dimvar.addattr('var_desc', '{:<80s}'.format('Timestep-valid flags:  (1) YYYYDDD or (2) HHMMSS'))
    dimvars.append(dimvar)
    for out_specie in out_species:
        dimvar = dataset.DimVariable()
        dimvar.name = out_specie
        dimvar.dtype = np.dtype.float
        dimvar.dims = vardims
        dimvar.addattr('long_name', "{:<16s}".format(out_specie))
        if out_specie in out_species_aer:
            dimvar.addattr('units', "{:<16s}".format('g/s'))
        else:
            dimvar.addattr('units', "{:<16s}".format('moles/s'))
        dimvar.addattr('var_desc', "{:<80s}".format("Hourly emission"))
        dimvars.append(dimvar)

    #Output file
    fn_out = dir_inter + '\GR_EMIS_{}_{}{:0>2d}'.format(mechanism_name, year, month)
    print('Create output data file...')
    print(fn_out)
    ncfile = dataset.addfile(fn_out, 'c', largefile=True)
    print('Define dimensions, global attributes and variables...')
    ncfile.nc_define(all_dims, global_attributes, dimvars, write_dimvars=False)
    
    #Times
    print('Write Times variable...')
    daytime = datetime.date(year=year, month=month, day=1)
    daytime1 = daytime.strftime("%Y%j")
    daytime2 = (daytime + datetime.timedelta(days=1)).strftime("%Y%j")
    t_out = np.zeros((tdim.length, vdim.length, ddim.length))
    for k in range(0, ddim.length):
        for i in range(0, tdim.length):
            if k == 0:
                if i != tdim.length - 1:
                    for j in range(0, vdim.length):
                        t_out[i, j, k] = int(daytime1)  
                else:
                    for j in range(0, vdim.length):
                        t_out[i, j, k] = int(daytime2)
            else:
                if i != tdim.length - 1:
                    for j in range(0, vdim.length):
                        t_out[i, j, k] = int(i * 10000)
                else:
                    for j in range(0, vdim.length):
                        t_out[i, j, k] = int(0)
    ncfile.write('TFLAG', t_out)
    
    #
    print('Write variable data except times...')
    for out_specie in out_species:
        data = np.zeros((tdim.length, zdim.length, ydim.length, xdim.length))
        dd = np.zeros((tdim.length, zdim.length, model_grid.y_num, model_grid.x_num))
        if out_specie in f_in.varnames:
            print(out_specie)
            for i in range(tdim.length):
                j = i
                if i == tdim.length - 1:
                    j = 0
                dd[i, :, :, :] = f_in[out_specie][j, :, :, :]
            #Conversion
            dd = transform(dd, model_grid, target_grid)
            #Set the fourth dimension 
            #dd = dd.reshape(12, 1, ydim.length, xdim.length)
            #Set default values
            dd[dd==np.nan] = 0
            data[:, :, :, :] = dd
        else:
            print('{} no data!'.format(out_specie))
        ncfile.write(out_specie, data)
    ncfile.close()
    f_in.close()
    print('Convert projection finished!')
    