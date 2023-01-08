from emips.utils import EmissionReader, SectorEnum
from emips.chem_spec import PollutantEnum
from emips.spatial_alloc import GridDesc
import os
from mipylib import geolib
from mipylib.dataset import addfile_ascii_grid


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

        fn = '2017_{:0>2d}_{}_{}.asc'.format(month, sector_name, pollutant_name)

        return os.path.join(self.dir_emission, fn)

    def read_emis(self, sector, pollutant, year, month):
        fn = self.get_emis_fn(sector, pollutant, month)
        print('File_in:{}'.format(fn))
        f = addfile_ascii_grid(fn)
        data = f['var'][:]
        return data

    def get_emis_grid(self):
        return GridDesc(geolib.projinfo(), x_orig=70.125, x_cell=0.25, x_num=320,
                        y_orig=10.125, y_cell=0.25, y_num=200)
