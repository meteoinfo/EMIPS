"""
Merge all pollutant emission files in one file for each sector.
"""

#Import
import os
import mipylib.numeric as np
from mipylib import dataset
from mipylib import geolib

import emips
from emips.utils import Sector, SectorEnum
from emips.chem_spec import Pollutant, PollutantEnum
from emips.spatial_alloc import GridDesc

def run(year, month, dir_inter):
    """
    Merge all pollutant emission files in one file for each sector.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) Data input and output path.
    """
    #Set sectors and pollutants
    sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY, \
        SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT, SectorEnum.SHIPS, \
        SectorEnum.AIR]
    pollutants = [PollutantEnum.BC, PollutantEnum.CH4, PollutantEnum.CO, \
        PollutantEnum.NH3, PollutantEnum.NOx, PollutantEnum.OC, PollutantEnum.PM2_5, \
        PollutantEnum.SO2, PollutantEnum.PM10, PollutantEnum.NMVOC]
    
    #Set model grids
    proj = geolib.projinfo()
    model_grid = GridDesc(proj, x_orig=70., x_cell=0.15, x_num=502,
        y_orig=15., y_cell=0.15, y_num=330)
    #Set dimensions
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]
    
    #Sector loop
    for sector in sectors:
        print('Sector: {}'.format(sector))
    
        #Set output sector emission file name
        outfn = os.path.join(dir_inter, \
            'emis_{}_{}_{}_hour.nc'.format(sector, year, month))
        print('Sector emission file: {}'.format(outfn))
    
        #Pollutant loop
        dimvars = []
        dict_spec = {}
        for pollutant in pollutants:
            #Read data in pollutant file
            if pollutant == PollutantEnum.NMVOC:
                fn = os.path.join(dir_inter, \
                    '{}_emis_lump_{}_{}_{}_hour.nc'.format(pollutant.name, \
                    sector.name, year, month))
            else:
                fn = os.path.join(dir_inter, \
                    '{}_emis_{}_{}_{}_hour.nc'.format(pollutant.name, \
                    sector.name, year, month))        
            if not os.path.exists(fn):    #No emission data
                print('\tAlarm! The file not exists: {}'.format(fn))
                continue
    
            print('\t{}'.format(fn))
            f = dataset.addfile(fn)
            for var in f.variables():
                if var.ndim == 3:
                    if dict_spec.has_key(var.name):
                        dict_spec[var.name].append(fn)
                    else:
                        dimvars.append(var)
                        dict_spec[var.name] = [fn]
    
        #Create output merged netcdf data file
        gattrs = dict(Conventions='CF-1.6', Tools='Created using MeteoInfo')
        ncfile = dataset.addfile(outfn, 'c')
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
        ncfile.close()

if __name__ == '__main__':
    #Set current working directory
    from inspect import getsourcefile
    dir_run = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
    if not dir_run in sys.path:
        sys.path.append(dir_run)
    dir_inter = r'D:\run_data\emips\run_htap\inter_data'

    #Run
    year = 2010
    month = 1
    run(year, month, dir_inter)