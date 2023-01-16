from emips.utils import EmissionReader, SectorEnum
from emips.chem_spec import PollutantEnum
from emips.spatial_alloc import GridDesc
import os
from mipylib import geolib
from mipylib.dataset import addfile


class MyEmissionReader(EmissionReader):

    def get_emis_fn(self, sector, pollutant, year, month):
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
        fn = 'meic-2017_%i_%s-%s.nc' % (month, sector_name, pollutant_name)
        return os.path.join(self.dir_emission, fn)

    def read_emis(self, sector, pollutant, year, month):
        fn = get_emis_fn(sector, pollutant, year, month)
        f = addfile(fn)
        data = f['z'][:]
        nx = 800
        ny = 500
        data = data.reshape(ny, nx)
        data = data[::-1,:]
        return data

    def get_emis_grid(self):
        return GridDesc(geolib.projinfo(), x_orig=70.05, x_cell=0.1, x_num=800,
                        y_orig=10.05, y_cell=0.1, y_num=500)


_emis_reader = MyEmissionReader(dir_emission='D:/KeyData/Emission/MEIC/2017/nc')


def get_emis_fn(sector, pollutant, year, month):
    return _emis_reader.get_emis_fn(sector, pollutant, year, month)


def read_emis(sector, pollutant, year, month):
    return _emis_reader.read_emis(sector, pollutant, year, month)


def get_emis_grid():
    return _emis_reader.get_emis_grid()


grid_areas = _emis_reader.get_emis_grid().grid_areas()
