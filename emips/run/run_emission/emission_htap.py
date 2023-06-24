from emips.utils import EmissionReader, SectorEnum
from emips.chem_spec import PollutantEnum
from emips.spatial_alloc import GridDesc
import os
from mipylib import geolib
from mipylib.dataset import addfile


class MyEmissionReader(EmissionReader):

    def get_emis_fn(self, sector, pollutant, year, month):
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
        return os.path.join(self.dir_emission, pollutant_name, fn)

    def read_emis(self, sector, pollutant, year, month):
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

    def get_emis_grid(self, sector=SectorEnum.INDUSTRY):
        return GridDesc(geolib.projinfo(), x_orig=0.05, x_cell=0.1, x_num=3600,
                        y_orig=-89.95, y_cell=0.1, y_num=1800)


_emis_reader = MyEmissionReader(dir_emission=r'M:\Data\Emission\EDGAR_HTAP\2010')


def get_emis_fn(sector, pollutant, year, month):
    return _emis_reader.get_emis_fn(sector, pollutant, year, month)


def read_emis(sector, pollutant, year, month):
    print("sector: {}".format(sector))
    return _emis_reader.read_emis(sector, pollutant, year, month)


def get_emis_grid(sector):
    return _emis_reader.get_emis_grid()


grid_areas = _emis_reader.get_emis_grid().grid_areas()
