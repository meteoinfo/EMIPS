"""
-----MEIC-----
"""
import os
from mipylib import geolib
from mipylib.dataset import addfile_ascii_grid

from emips.chem_spec import PollutantEnum
from emips.spatial_alloc import GridDesc
from emips.utils import SectorEnum

__all__ = ['dir_emission', 'emis_grid', 'grid_areas', 'get_emis_fn', 'read_emis']

dir_emission = r'M:\Data'

emis_grid = GridDesc(geolib.projinfo(), x_orig=70.125, x_cell=0.25, x_num=320,
                     y_orig=10.125, y_cell=0.25, y_num=200)

# Calculate emission grid areas
grid_areas = emis_grid.grid_areas()  # square meters (array)


def get_emis_fn(sector, pollutant, month):
    """
    Get emission file path.

    :param sector: (*Sector*) The emission sector.
    :param pollutant: (*Pollutant*) The pollutant.
    :param month: (*int*) The month.
    :returns: (*string*) Emission file path.
    """
    sector_name = sector.name.lower()
    if sector == SectorEnum.ENERGY:
        sector_name = 'power'
    elif sector == SectorEnum.TRANSPORT:
        sector_name = 'transportation'
    pollutant_name = pollutant.name.upper()
    if pollutant == PollutantEnum.PM2_5:
        pollutant_name = 'PM25'
    elif pollutant == PollutantEnum.NMVOC:
        pollutant_name = 'VOC'
    fn = '2017_{:0>2d}_{}_{}.asc'.format(month, sector_name, pollutant_name)
    return os.path.join(dir_emission, fn)


def read_emis(sector, pollutant, month):
    """
    Read emission data array.

    :param sector: (*Sector*) The sector.
    :param pollutant: (*Pollutant*) The pollutant.
    :param month: (*int*) The month.
    :returns: (*array*) Emission data array.
    """
    fn = get_emis_fn(sector, pollutant, month)
    print('File_in:{}'.format(fn))
    f = addfile_ascii_grid(fn)
    data = f['var'][:]
    return data
