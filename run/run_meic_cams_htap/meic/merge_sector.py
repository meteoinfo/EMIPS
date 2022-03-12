import os
import mipylib.numeric as np
from mipylib import dataset
from mipylib import geolib

import emips
from emips.utils import Sector, SectorEnum
from emips.chem_spec import Pollutant, PollutantEnum
from emips.spatial_alloc import GridDesc

def run(year, month, dir_inter, model_grid):
    """
    Merge all pollutant emission files in one file for each sector.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) Data input and output path.
    :param model_grid: (*GridDesc*) Model data grid describe.
    """
    #Set sectors and pollutants
    sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY,
        SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT]
    pollutants = [PollutantEnum.BC, PollutantEnum.CO, PollutantEnum.NH3, \
        PollutantEnum.NOx, PollutantEnum.OC, PollutantEnum.PM2_5, \
        PollutantEnum.SO2, PollutantEnum.PMcoarse, PollutantEnum.PM10more, \
        PollutantEnum.NMVOC]

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
            'emis_{}_{}_{}_hour.nc'.format(sector.name, year, month))
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
            print('\t{}'.format(fn))
            #Determine whether the PM10more file exists 
            if os.path.exists(fn):
                f = dataset.addfile(fn)
            else:
                print('File not exist: {}'.format(fn))
                continue
                
            for var in f.variables():
                if var.ndim == 3:
                    if dict_spec.has_key(var.name):
                        dict_spec[var.name].append(fn)
                    else:
                        dimvars.append(var)
                        dict_spec[var.name] = [fn]
    
        #Create output merged netcdf data file
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
        ncfile.close()

if __name__ == '__main__':
    #Set year, month and data path
    year = 2016
    month = 6
    dir_inter = r'G:\emips_data\global_1\MEIC\2016\{}{:>02d}'.format(year, month)
    if not os.path.exists(dir_inter):
        os.mkdir(dir_inter)

    #Set model grids
    proj = geolib.projinfo()
    model_grid = GridDesc(proj, x_orig=0., x_cell=1, x_num=360,
        y_orig=-89.75, y_cell=1, y_num=180)

    #Run
    run(year, month, dir_inter, model_grid)
