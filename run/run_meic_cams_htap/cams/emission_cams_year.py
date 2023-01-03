"""
-----CAMS-----
"""
from emips.chem_spec import Pollutant, PollutantEnum
from emips.utils import SectorEnum
from emips.spatial_alloc import GridDesc
import os
import datetime
from mipylib.dataset import addfile
from mipylib import geolib
import mipylib.numeric as np

__all__ = ['dir_emission', 'emis_grid', 'grid_areas', 'get_emis_fn', 'read_emis']

dir_emission = r'M:\Data'


def get_emis_version(sector):
    """
    Get emission data version.

    :param sector: (*Sector*) The emission sector.
    """
    version = "ANT_v4.2"
    if sector == SectorEnum.AIR:
        version = "AIR_v1.1"
    elif sector == SectorEnum.SHIPS:
        version = "SHIP_v2.1"
    elif sector == SectorEnum.BIOMASS:
        version = "BIO_v2.1"

    return version


def get_emis_fn(sector, pollutant, year, month):
    """
    Get emission file path.

    :param sector: (*Sector*) The emission sector.
    :param pollutant: (*Pollutant*) The pollutant.
    :param year: (*int*) The year.
    :param month: (*int*) The month.
    :returns: (*string*) Emission file path.
    """
    if pollutant == PollutantEnum.BC:
        pollutant_name = 'black-carbon'
    if pollutant == PollutantEnum.CH4:
        pollutant_name = 'methane'
    if pollutant == PollutantEnum.CO:
        pollutant_name = 'carbon-monoxide'
    if pollutant == PollutantEnum.NH3:
        pollutant_name = 'ammonia'
    if pollutant == PollutantEnum.NOx:
        pollutant_name = 'nitrogen-oxides'
    if pollutant == PollutantEnum.OC:
        pollutant_name = 'organic-carbon'
    if pollutant == PollutantEnum.SO2:
        pollutant_name = 'sulphur-dioxide'
    if pollutant == PollutantEnum.NMVOC:
        pollutant_name = 'non-methane-vocs'

    if sector == SectorEnum.SHIPS:
        if pollutant == PollutantEnum.BC:
            pollutant_name = 'elemental-carbon'
        elif pollutant == PollutantEnum.SO2:
            pollutant_name = 'sulphur-oxides'
        elif pollutant == PollutantEnum.NMVOC:
            pollutant_name = 'vocs-all'
    version = get_emis_version(sector)
    fn = 'CAMS-GLOB-{}_{}_{}.nc'.format(version, pollutant_name, year)
    return os.path.join(dir_emission, str(year), fn)


def get_varnames(sector):
    """
    Get variable names from sector.

    :param sector: (*Sector*) The sector.

    :returns: (*list of str*) Variable names.
    """
    varnames = []
    if sector == SectorEnum.AGRICULTURE:
        varnames = ['agl', 'ags', 'awb']
    elif sector == SectorEnum.ENERGY:
        varnames = ['ene']
    elif sector == SectorEnum.INDUSTRY:
        varnames = ['ind', 'slv', 'fef']
    elif sector == SectorEnum.RESIDENTIAL:
        varnames = ['res']
    elif sector == SectorEnum.SHIPS:
        varnames = ['sum']
    elif sector == SectorEnum.AIR:
        varnames = ['avi']
    elif sector == SectorEnum.TRANSPORT:
        varnames = ['tro', 'tnr']
    elif sector == SectorEnum.WASTE_TREATMENT:
        varnames = ['swd']
    elif sector == SectorEnum.BIOMASS:
        varnames = ['emiss_bio_monthly']

    return varnames


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
        varnames = get_varnames(sector)
        if len(varnames) == 0:
            return None

        t = datetime.datetime(year, month, 15)
        data = None
        for vname in varnames:
            if sector == SectorEnum.AIR:
                dd = f[vname][month - 1]
                dd = dd.sum(axis=0)
            else:
                dd = f[vname][month - 1]
            if data is None:
                data = dd
            else:
                data = data + dd
        return data
    else:
        print('Alarm! Emission data file not exists: {}'.format(fn))
        return None


def get_emis_grid(sector):
    """
    Get emission grid set

    :param sector: (*Sector*) The sector.

    :returns: (*GridSet*) Emission grid set.
    """
    if sector == SectorEnum.AIR:
        emis_grid = GridDesc(geolib.projinfo(), x_orig=-179.75, x_cell=0.5, x_num=720,
                             y_orig=-89.75, y_cell=0.5, y_num=360)
    elif sector == SectorEnum.BIOMASS:
        emis_grid = GridDesc(geolib.projinfo(), x_orig=-180.0, x_cell=0.25, x_num=1440,
                             y_orig=-90.0, y_cell=0.25, y_num=720)
    elif sector == SectorEnum.SHIPS:
        emis_grid = GridDesc(geolib.projinfo(), x_orig=-180.0, x_cell=0.25, x_num=1440,
                             y_orig=-89.75, y_cell=0.25, y_num=720)
    else:
        emis_grid = GridDesc(geolib.projinfo(), x_orig=-179.95, x_cell=0.1, x_num=3600,
                             y_orig=-89.95, y_cell=0.1, y_num=1800)

    return emis_grid


def lonpivot(data, pivot, emis_grid):
    """
    Pivots an array about a user-specified longitude.

    :param data: (*array*) array data.
    :param pivot: (*float*) The longitude value around which to pivot. 
    :param emis_grid: (*GridSet*) emission grid set.

    :returns: result data array and emission grid.
    """
    rdata = data.lonpivot(pivot)
    lon = emis_grid.get_x_value(pivot)
    rgrid = GridDesc(emis_grid.proj, x_orig=lon, x_cell=emis_grid.x_cell, x_num=emis_grid.x_num,
                     y_orig=emis_grid.y_orig, y_cell=emis_grid.y_cell, y_num=emis_grid.y_num)
    return rdata, rgrid


def grid_expand(data, emis_grid):
    """
    Emission data grid expand to avoid NaN values in interpolation process.

    :param data: (*array*) emission data array (2D).
    :param emis_grid: (*GridSet*) emission grid set.

    :returns: Expanded data array and emission grid set.
    """
    ny, nx = data.shape
    rdata = np.zeros((ny + 2, nx + 2))
    rdata[1:-1, 1:-1] = data
    rdata[0, 1:-1] = data[0, :]
    rdata[-1, 1:-1] = data[-1, :]
    rdata[1:-1, 0] = data[:, 0]
    rdata[1:-1, -1] = data[:, -1]
    rdata[0, 0] = data[0, 0]
    rdata[-1, 0] = data[-1, 0]
    rdata[0, -1] = data[0, -1]
    rdata[-1, -1] = data[-1, -1]

    x = emis_grid.x_orig - emis_grid.x_delta
    y = emis_grid.y_orig - emis_grid.y_delta
    rgrid = GridDesc(emis_grid.proj, x_orig=x, x_cell=emis_grid.x_cell, x_num=emis_grid.x_num + 2,
                     y_orig=y, y_cell=emis_grid.y_cell, y_num=emis_grid.y_num + 2)

    return rdata, rgrid
