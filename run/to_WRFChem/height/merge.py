from emips.spatial_alloc import GridDesc
from collections import OrderedDict
from mipylib import dataset
import mipylib.numeric as np
import os

out_species_aer = ['PEC', 'POA', 'PMFINE', 'PNO3', 'PSO4', 'PMC']

def run_merge(year, month, dir_inter, model_grid, sectors, z):
    """
    Combine all sectors into one file

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param sectors: (*list*) Sectors that needs to be merged.
    :param z: (*int*) The zdim of the output data.
    """
    print('Define dimension and global attributes...')
    tdim = np.dimension(np.arange(24), 'hour')
    zdim = np.dimension(np.arange(z), 'emissions_zdim')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, zdim, ydim, xdim]
    #Set the definition of the output variable
    print('Define variables...')
    dimvars = []
    dict_spec = {}
    print('Add files...')
    for sector in sectors:
        fn = dir_inter + '\emis_{}_{}_{}_hour_height.nc'.format(sector, year, month)
        if os.path.exists(fn):
            print(fn)
            f = dataset.addfile(fn)
            for var in f.variables():
                if var.ndim == 4:
                    if dict_spec.has_key(var.name):
                        dict_spec[var.name].append(fn)
                    else:
                        dict_spec[var.name] = [fn]
            for var in f.varnames():
                if var == 'lat' or var == 'lon':
                        continue
                else:
                    dimvar = dataset.DimVariable()
                    dimvar.name = var
                    dimvar.dtype = np.dtype.float
                    dimvar.dims = dims
                    dimvar.addattr('description', "EMISSION_{}".format(var))
                    if var in out_species_aer:
                        dimvar.addattr('units', 'g/m2/s')
                    else:
                        dimvar.addattr('units', 'mole/m2/s')
                dimvars.append(dimvar)   
            f.close()
        else:
            print('File not exist: {}'.format(fn))
            continue
            
    #Set dimension and define ncfile 
    out_fn = dir_inter + '\emis_{}_{}_hour.nc'.format(year, month)
    gattrs = OrderedDict()
    gattrs['Conventions'] = 'CF-1.6'
    gattrs['Tools'] = 'Created using MeteoInfo'
    print('Create output data file...')
    ncfile = dataset.addfile(out_fn, 'c', largefile=True)
    ncfile.nc_define(dims, gattrs, dimvars)
    #read, merge and output
    print('Write variables data...')
    for sname, fns in dict_spec.iteritems():
        print(sname)
        spec_data = np.zeros((tdim.length, z, ydim.length, xdim.length))
        dd = np.zeros((tdim.length, z, ydim.length, xdim.length))
        for fn in fns:
            f = dataset.addfile(fn)
            dd = f[sname][:]
            #turn nan to zero
            dd[dd==np.nan] = 0.0
            if spec_data.sum() == 0.0:
                spec_data = dd
            else:
                spec_data = spec_data + dd
            f.close()
        ncfile.write(sname, spec_data)
    ncfile.close()
    print('Merge data finished!')

if __name__ == '__main__':
    #set parameter 
    year = 2017
    month = 1
    dir_inter = r'G:\emips_data\region_0.1\MEIC\2017\{}{:>02d}'.format(year, month)
    model_grid = GridDesc(geolib.projinfo(), x_orig=70., x_cell=0.1, x_num=751,
            y_orig=15., y_cell=0.1, y_num=501)
    #run
    run_merge(year, month, dir_inter, model_grid)
    
