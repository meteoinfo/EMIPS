"""
-----HTAP-----
"""
from emips.chem_spec import Pollutant, PollutantEnum
from emips.utils import SectorEnum
from emips.spatial_alloc import GridDesc
import os
from mipylib.dataset import addfile
from mipylib import geolib

__all__ = ['dir_emission', 'emis_grid', 'grid_areas', 'get_emis_fn', 'read_emis']

dir_emission = r'M:\test'

emis_grid = GridDesc(geolib.projinfo(), x_orig=0.05, x_cell=0.1, x_num=3600,
    y_orig=-89.95, y_cell=0.1, y_num=1800)

#Calculate emission grid areas
grid_areas = emis_grid.grid_areas()    #square meters

def get_emis_fn(sector, pollutant, year, month):
    """
    Get emission file path.

    :param sector: (*Sector*) The emission sector.
    :param pollutant: (*Pollutant*) The pollutant.
    :param year: (*int*) The year.
    :param month: (*int*) The month.
    :returns: (*string*) Emission file path.
    """
    pollutant_name = pollutant.name.upper()
    if pollutant == PollutantEnum.CH4:    #Only has yearly emission
        fn = 'sum_v42_FT2010_{}_{}_IPCC_{}.0.1x0.1.nc'.format(pollutant_name,
            year, sector.name.upper())
    else:
        if pollutant == PollutantEnum.PM2_5:
            pollutant_name = 'PM2.5'
        if sector in [SectorEnum.AIR, SectorEnum.SHIPS]:  #Only has yearly emission
            fn = 'edgar_HTAP_{}_emi_{}_{}.0.1x0.1.nc'.format(pollutant_name, 
                sector.name.upper(), year)
        else:
            fn = 'edgar_HTAP_{}_emi_{}_{}_{}.0.1x0.1.nc'.format(pollutant_name, 
                sector.name.upper(), year, month)
    return os.path.join(dir_emission, pollutant_name, fn)

def read_emis(sector, pollutant, year, month):
    """
    Read emission data array.

    :param sector: (*Sector*) The sector.
    :param pollutant: (*Pollutant*) The pollutant.
    :param year: (*int*) The year.
    :param month: (*int*) The month.
    :returns: (*array*) Emission data array.
    """
    fn = get_emis_fn(sector, pollutant, year, month)
    if os.path.exists(fn):
        print('Emission data file: {}'.format(fn))
        f = addfile(fn)
        pollutant_name = pollutant.name.lower()
        if pollutant == PollutantEnum.PM2_5:
            pollutant_name = 'pm2.5'
        vname = 'emi_{}'.format(pollutant_name)
        data = f[vname][:]
        return data
    else:
        print('Alarm! Emission data file not exists: {}'.format(fn))
        return None