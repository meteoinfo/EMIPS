from emips.chem_spec import GridSpecReader
from emips.utils import SectorEnum
from emips.spatial_alloc import GridDesc
import os
from mipylib import dataset
from mipylib import numeric as np


def get_sector_str(sector):
    """
    Get sector string.
    :param sector: (*Sector*) The sector.
    :return: (*str*) Sector string.
    """
    if sector == SectorEnum.INDUSTRY:
        return "inc"
    elif sector == SectorEnum.AGRICULTURE:
        return "agr"
    elif sector == SectorEnum.ENERGY:
        return "pow"
    elif sector == SectorEnum.RESIDENTIAL:
        return "res"
    elif sector in [SectorEnum.TRANSPORT, SectorEnum.AIR, SectorEnum.SHIPS]:
        return "tra"
    else:
        return None


class RetroGridSpecReader(GridSpecReader):

    def get_spec_fn(self, sector):
        self.sector = sector
        sector_str = get_sector_str(sector)
        fn = os.path.join(self.dir_grid, 'retro_nmvoc_ratio_{}_2000_0.1deg.nc'.format(sector_str))
        return fn

    def get_spec_vars(self, sector, dims):
        fn = self.get_spec_fn(sector)
        self.f = dataset.addfile(fn)
        spec_vars = []
        for var in self.f.variables:
            if var.ndim == 2:
                spec_var = dataset.DimVariable()
                spec_var.name = var.name
                spec_var.dtype = np.dtype.float
                spec_var.dims = dims
                spec_var.addattr('units', 'g/m2/s')
                spec_vars.append(spec_var)

        return spec_vars

    def read_spec(self, sector, spec_var):
        if self.sector != sector or self.f is None:
            fn = self.get_spec_fn(sector)
            self.f = dataset.addfile(fn)

        return self.f[spec_var.name][:]

    def get_spec_grid(self):
        return GridDesc(x_orig=0.05, x_cell=0.1, x_num=3600,
                        y_orig=-89.95, y_cell=0.1, y_num=1800)


_grid_spec_reader = RetroGridSpecReader(dir_grid="Z:\chen\Research\EMIPS\Grid_speciation_data(VOC)")


def get_spec_fn(sector):
    return _grid_spec_reader.get_spec_fn(sector)


def get_spec_vars(sector, dims):
    return _grid_spec_reader.get_spec_vars(sector, dims)


def read_spec(sector, spec_var):
    return _grid_spec_reader.read_spec(sector, spec_var)


def get_spec_grid():
    return _grid_spec_reader.get_spec_grid()
