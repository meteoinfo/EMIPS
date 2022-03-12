from emips.spatial_alloc import GridDesc
from collections import OrderedDict
from mipylib import dataset
import mipylib.numeric as np
import os

################################
#set the sector to be allocated
sectors_al = ['energy', 'industry']
################################
out_species_unit = ['PEC', 'POA', 'PMFINE', 'PNO3', 'PSO4', 'PMC']

def run_allocate(year, month, dir_inter, model_grid, sectors, z):
    """
    Assign data to different heights.
    If not specified, data is allocated to the first layer.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param sectors: (*GridDesc*) The sectors need to be processed.
    :param z: (*int*) The zdim of the output data.
    """
    print('Define dimension and global attributes...')
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    zdim = np.dimension(np.arange(z), 'emissions_zdim')
    dims = [tdim, zdim, ydim, xdim]
    
    gattrs = OrderedDict()
    gattrs['Conventions'] = 'CF-1.6'
    gattrs['Tools'] = 'Created using MeteoInfo'
    
    for sector in sectors:
        fn = dir_inter + '\emis_{}_{}_{}_hour.nc'.format(sector, year, month)
        print('File input: {}'.format(fn))
        dimvars = []
        if os.path.exists(fn):
            f = dataset.addfile(fn)
            for var in f.varnames():
                if var == 'lat' or var == 'lon':
                    continue
                else:
                    dimvar = dataset.DimVariable()
                    dimvar.name = var
                    dimvar.dtype = np.dtype.float
                    dimvar.dims = dims
                    dimvar.addattr('description', "EMISSION_{}".format(var))
                    if var in out_species_unit:
                        dimvar.addattr('units', 'g/m2/s')
                    else:
                        dimvar.addattr('units', 'mole/m2/s')
                    dimvars.append(dimvar)
                    
            print('Create output data file...')
            out_fn = dir_inter + '\emis_{}_{}_{}_hour_height.nc'.format(sector, year, month)
            ncfile = dataset.addfile(out_fn, 'c', largefile=True)
            ncfile.nc_define(dims, gattrs, dimvars)
            
            data = np.zeros((tdim.length, z, ydim.length, xdim.length))
            dd = np.zeros((tdim.length, z, ydim.length, xdim.length))
            #read, merge and output
            if sector in sectors_al:
                print('Allocating: {}'.format(sector))
            else:
                print('Do not need to be allocated: {}'.format(sector))
            print('Write data to file...')
            for var in f.varnames():
                if var == 'lat' or var == 'lon':
                    continue
                else:
                    print(var)
                    dd[:, 0, :, :] = f[var][:]
                    if sector in sectors_al:
                        if sector == 'energy':
                            data[:, 1, :, :] = dd[:, 0, :, :] * 0.1
                            data[:, 2, :, :] = dd[:, 0, :, :] * 0.1
                            data[:, 3, :, :] = dd[:, 0, :, :] * 0.3
                            data[:, 4, :, :] = dd[:, 0, :, :] * 0.2
                            data[:, 5, :, :] = dd[:, 0, :, :] * 0.2
                            data[:, 6, :, :] = dd[:, 0, :, :] * 0.1
                        if sector == 'industry':
                            data[:, 0, :, :] = dd[:, 0, :, :] * 0.5
                            data[:, 1, :, :] = dd[:, 0, :, :] * 0.3
                            data[:, 2, :, :] = dd[:, 0, :, :] * 0.2
                    else:
                        data[:, 0, :, :] = dd[:, 0, :, :]
                    #Turn nan to zero
                    data[data==np.nan] = 0
                    ###test###
                    '''
                    if sector == 'energy':
                        data[:, 0, :, :] = 0  
                    '''
					###test###					
                ncfile.write(var, data)
            ncfile.close()
            f.close()
        else:
            print('File not exist: {}'.format(fn))
            continue
    print('Allocate of height finished!')
    
if __name__ == '__main__':
    #set parameter 
    year = 2017
    month = 1
    dir_inter = r'G:\emips_data\region_0.1\MEIC\2017\{}{:>02d}'.format(year, month)
    model_grid = GridDesc(geolib.projinfo(), x_orig=70., x_cell=0.1, x_num=751,
            y_orig=15., y_cell=0.1, y_num=501)
    z = 8
    #run
    run_allocate(year, month, dir_inter, model_grid, z)
        