from emips.spatial_alloc import GridDesc
from collections import OrderedDict
from mipylib import dataset
import mipylib.numeric as np
import os
from emips.utils import emis_util
import emips

out_species_unit = ['PEC', 'POA', 'PMFINE', 'PNO3', 'PSO4', 'PMC']


def run(year, month, dir_inter, model_grid, sectors, z, z_file):
    """
    Allocate data to different heights.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param sectors: (*GridDesc*) The sectors need to be processed.
    :param z: (*int*) The zdim of the output data.
    :param z_file: (*string*) The path of the vertical allocate file.
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
        fn = dir_inter + '\emis_{}_{}_{}_hour.nc'.format(sector.name, year, month)
        print('File input: {}'.format(fn))
        dimvars = []
        if os.path.exists(fn):
            f = dataset.addfile(fn)
            for var in f.varnames:
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

            out_fn = dir_inter + '\emis_{}_{}_{}_hour_height.nc'.format(sector.name, year, month)
            print('Create output data file:{}'.format(out_fn))
            ncfile = dataset.addfile(out_fn, 'c', largefile=True)
            ncfile.nc_define(dims, gattrs, dimvars)

            data = np.zeros((tdim.length, z, ydim.length, xdim.length))
            dd = np.zeros((tdim.length, z, ydim.length, xdim.length))
            # get vertical profiles
            scc = emis_util.get_scc(sector)
            vertical_pro = emips.vertical_alloc.read_file(z_file, scc)
            # read, merge and output
            if round(vertical_pro.get_ratios()[0], 2) != 1.0:
                print('Allocating: {}'.format(sector.name))
            else:
                print('Do not need to be allocated: {}'.format(sector.name))
            print('Write data to file...')
            for var in f.varnames:
                if var == 'lat' or var == 'lon':
                    continue
                else:
                    print(var)
                    dd[:, 0, :, :] = f[var][:]
                    if round(vertical_pro.get_ratios()[0], 2) == 1.0:
                        data[:, 0, :, :] = dd[:, 0, :, :]
                    else:
                        for lay in np.arange(len(vertical_pro.get_ratios())):
                            data[:, lay, :, :] = dd[:, 0, :, :] * vertical_pro.get_ratios()[lay]
                    # Turn nan to zero
                    data[data == np.nan] = 0
                ncfile.write(var, data)
            ncfile.close()
            f.close()
        else:
            print('File not exist: {}'.format(fn))
            continue
    print('Allocate of height finished!')
