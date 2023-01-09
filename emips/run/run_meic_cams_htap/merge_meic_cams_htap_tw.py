import emips
from emips.utils import Sector, SectorEnum
from mipylib.dataset import DimVariable, addfile
import shutil
from mipylib import geolib
import os
import mipylib.numeric as np


def run(dire, year, months, model_grid, mechanism_name):
    """
    Merge EMIPS output emission data of MEIC CAMS and HTAP data
    Applicable to the situation that MEIC data are nan outside China, and 0 in Taiwan!!!

    :param year: (*int*) Year.
    :param months: (*list*) Months.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param mechanism_name: (*string*) mechanism's name.
    """
    print('-----------------------------------')
    print('----Merge output data(tw).....-----')
    print('-----------------------------------')
    # Set directories

    dir_meic1 = os.path.join(dire, mechanism_name, r'MEIC', str(year))
    dir_cams1 = os.path.join(dire, mechanism_name, r'CAMS', str(year))
    dir_htap1 = os.path.join(dire, mechanism_name, r'HTAP\2010')
    dir_out1 = os.path.join(dire, mechanism_name, r'merge', str(year))
    if not os.path.exists(dir_out1):
        os.makedirs(dir_out1)
    # Set sectors
    sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY, \
               SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT, SectorEnum.SHIPS, \
               SectorEnum.AIR]

    # Set dimensions
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]

    # Add data of taiwan area use CAMS/HTAP data
    tw = geolib.shaperead('taiwan.shp')

    for month in months:
        print('##########')
        print('Month: {}'.format(month))
        print('##########')

        dir_meic = os.path.join(dir_meic1, '{}{:>02d}'.format(year, month))
        dir_cams = os.path.join(dir_cams1, '{}{:>02d}'.format(year, month))
        dir_htap = os.path.join(dir_htap1, '{}{:>02d}'.format(2010, month))
        dir_out = os.path.join(dir_out1, '{}{:>02d}'.format(year, month))
        if not os.path.exists(dir_out):
            os.mkdir(dir_out)
        print('------------------Filepath------------------')
        print('dir_meic: {}\ndir_cams: {}\ndir_htap: {}\ndir_out: {}'.format(dir_meic, dir_cams, dir_htap, dir_out))
        # Sector loop
        for sector in sectors:
            print('############')
            print(sector.name)
            print('############')

            # MEIC data file
            fn_meic = os.path.join(dir_meic, 'emis_{}_{}_{}_hour.nc'.format(sector.name, year, month))
            # CAMS data file
            fn_cams = os.path.join(dir_cams, 'emis_{}_{}_{}_hour.nc'.format(sector.name, year, month))
            # HTAP data file
            fn_htap = os.path.join(dir_htap, 'emis_{}_{}_{}_hour.nc'.format(sector.name, 2010, month))
            # Output data file
            fn_out = os.path.join(dir_out, 'emis_{}_{}_{}_hour.nc'.format(sector.name, year, month))

            if os.path.exists(fn_meic) and (not os.path.exists(fn_cams)):
                shutil.copyfile(fn_meic, fn_out)
                print('Data from MEIC...')
            elif os.path.exists(fn_cams) and (not os.path.exists(fn_meic)):
                shutil.copyfile(fn_cams, fn_out)
                print('Data from CAMS...')
            else:
                f_meic = addfile(fn_meic)
                f_cams = addfile(fn_cams)
                f_htap = addfile(fn_htap)
                # Create output netcdf file
                ncfile = addfile(fn_out, 'c', largefile=True)
                # Set global attribute
                gattrs = dict(Conventions='CF-1.6', Tools='Created using MeteoInfo')
                # Get all variable
                dimvars = []
                varnames = []
                for var in f_meic.variables:
                    if var.ndim == 3:
                        varnames.append(var.name)
                        dimvar = DimVariable()
                        dimvar.name = var.name
                        dimvar.dtype = var.dtype
                        dimvar.dims = dims
                        dimvar.attributes = var.attributes
                        dimvars.append(dimvar)
                for var in f_htap.variables:
                    if var.ndim == 3 and (not var.name in varnames):
                        varnames.append(var.name)
                        dimvar = DimVariable()
                        dimvar.dtype = var.dtype
                        dimvar.name = var.name
                        dimvar.dims = dims
                        dimvar.attributes = var.attributes
                        dimvars.append(dimvar)
                # Define dimensions, global attributes and variables
                ncfile.nc_define(dims, gattrs, dimvars)

                # Write variable values
                for varname in varnames:
                    print('\t{}'.format(varname))
                    data = None
                    tda = np.zeros((24, len(model_grid.y_coord), len(model_grid.x_coord)))
                    if varname in f_meic.varnames:
                        data = f_meic[varname][:]
                    if varname in f_cams.varnames:
                        data1 = f_cams[varname][:]
                        for i in range(24):
                            tda[i] = data1[i].maskout(tw.shapes())
                        tda[tda == np.nan] = 0
                        if data is None:
                            data = data1
                        else:
                            mask = data.copy()
                            mask[mask != np.nan] = 0
                            mask[mask == np.nan] = 1
                            data[data == np.nan] = 0
                            data = data1 * mask + data

                            data = data + tda
                    elif varname in f_htap.varnames:
                        data1 = f_htap[varname][:]
                        for i in range(24):
                            tda[i] = data1[i].maskout(tw.shapes())
                        tda[tda == np.nan] = 0
                        if data is None:
                            data = data1
                        else:
                            mask = data.copy()
                            mask[mask != np.nan] = 0
                            mask[mask == np.nan] = 1
                            data[data == np.nan] = 0
                            data = data1 * mask + data
                            data = data + tda

                    ncfile.write(varname, data)

                # Close file
                f_meic.close()
                f_cams.close()
                f_htap.close()
                ncfile.close()

    print('---------------------------------------')
    print('-----Merge output data completed!------')
    print('---------------------------------------')


if __name__ == '__main__':
    from emips.spatial_alloc import GridDesc
    import time

    time_start = time.time()

    # Settings
    year = 2017
    months = [1]
    proj = geolib.projinfo()
    model_grid = GridDesc(proj, x_orig=64., x_cell=0.25, x_num=324,
                          y_orig=15., y_cell=0.25, y_num=180)
    mechanism_name = 'radm2'
    dire = r'G:\test_new'
    run(dire, year, months, model_grid, mechanism_name)

    time_end = time.time()
    time = (time_end - time_start) / 60
    print('Time: {:.2f}min'.format(time))
