"""
-----MEIC-----
"""
import mipylib.numeric as np
import os
from mipylib import dataset

from emips.chem_spec import PollutantEnum
from emips.utils import SectorEnum


def run(year, month, dir_inter, model_grid):
    """
    Merge all pollutant emission files in one file for each sector.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) Data input and output path.
    :param model_grid: (*GridDesc*) Model data grid describe.
    """
    # Set sectors and pollutants
    sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY,
               SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT]

    pollutants = [PollutantEnum.BC, PollutantEnum.CO, PollutantEnum.NH3,
                  PollutantEnum.NOx, PollutantEnum.OC, PollutantEnum.PM2_5,
                  PollutantEnum.SO2, PollutantEnum.PM10, PollutantEnum.NMVOC]

    # Set dimensions
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]

    # Sector loop
    for sector in sectors:
        print('-----{}-----'.format(sector.name))

        # Set output sector emission file name
        outfn = os.path.join(dir_inter,
                             'emis_{}_{}_{}_hour.nc'.format(sector.value.name, year, month))
        print('File_out: {}'.format(outfn))

        # Pollutant loop
        dimvars = []
        dict_spec = {}
        for pollutant in pollutants:
            # Read data in pollutant file
            if pollutant == PollutantEnum.NMVOC:
                fn = os.path.join(dir_inter,
                                  '{}_emis_lump_{}_{}_{}_hour.nc'.format(pollutant.value.name,
                                                                         sector.value.name, year, month))
            else:
                fn = os.path.join(dir_inter,
                                  '{}_emis_{}_{}_{}_hour.nc'.format(pollutant.value.name,
                                                                    sector.value.name, year, month))
            print('File_in: {}'.format(fn))
            f = dataset.addfile(fn)

            for var in f.variables:
                if var.ndim == 3:
                    if dict_spec.has_key(var.name):
                        dict_spec[var.name].append(fn)
                    else:
                        dimvars.append(var)
                        dict_spec[var.name] = [fn]

        # Create output merged netcdf data file
        gattrs = dict(Conventions='CF-1.6', Tools='Created using MeteoInfo')
        ncfile = dataset.addfile(outfn, 'c', largefile=True)
        ncfile.nc_define(dims, gattrs, dimvars)
        for sname, fns in dict_spec.iteritems():
            spec_data = None
            for fn in fns:
                f = dataset.addfile(fn)
                if spec_data is None:
                    spec_data = f[sname][:]
                else:
                    spec_data = spec_data + f[sname][:]
            ncfile.write(sname, spec_data)
        f.close()
        ncfile.close()
