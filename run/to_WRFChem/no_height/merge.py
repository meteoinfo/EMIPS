from emips.spatial_alloc import GridDesc
from collections import OrderedDict
from mipylib import dataset
import mipylib.numeric as np
import os


def run_merge(year, month, dir_inter, model_grid, sectors):
    """
    Combine all sectors into one file

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param sectors: (*list*) Sectors that needs to be merged.
    """
    #Set the definition of the output variable
    print('Define variables...')
    dimvars = []
    dict_spec = {}
    for sector in sectors:
        fn = dir_inter + '\emis_{}_{}_{}_hour.nc'.format(sector, year, month)
        if os.path.exists(fn):
            f = dataset.addfile(fn)
            for var in f.variables():
                if var.ndim == 3:
                    if dict_spec.has_key(var.name):
                        dict_spec[var.name].append(fn)
                    else:
                        dimvars.append(var)
                        dict_spec[var.name] = [fn]
            f.close()
        else:
            print('File not exist: {}'.format(fn))
            continue
    #Set dimension and define ncfile
    print('Define dimension and global attributes...')
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]
    out_fn = dir_inter + '\emis_{}_{}_hour.nc'.format(year, month)
    gattrs = OrderedDict()
    gattrs['Conventions'] = 'CF-1.6'
    gattrs['Tools'] = 'Created using MeteoInfo'
    print('Create output data file...')
    ncfile = dataset.addfile(out_fn, 'c', largefile=True)
    ncfile.nc_define(dims, gattrs, dimvars)
    #read, merge and output
    print('Write variable data...')
    for sname, fns in dict_spec.iteritems():
        print(sname)
        spec_data = None
        dd = None
        for fn in fns:
            f = dataset.addfile(fn)
            dd = f[sname][:]
            #turn nan to zero
            dd[dd==np.nan] = 0
            if spec_data is None:
                spec_data = dd
            else:
                spec_data = spec_data + dd
            f.close()
        ncfile.write(sname, spec_data)
    ncfile.close()
    print('Merge sector data finished!')

if __name__ == '__main__':
    #set parameter 
    year = 2015
    month = 2
    dir_inter = r'D:\chen\MEIC_data\radm2_wrfchem_test\{}{:>02d}'.format(year, month)
    model_grid = GridDesc(geolib.projinfo(), x_orig=70., x_cell=0.15, x_num=502,
            y_orig=15., y_cell=0.15, y_num=330)
    #run
    run_merge(year, month, dir_inter, model_grid)
    
