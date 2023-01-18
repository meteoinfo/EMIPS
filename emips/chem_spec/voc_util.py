from abc import ABCMeta, abstractmethod

__all__ = ["GridSpecReader"]


class GridSpecReader(object):

    __metaclass__ = ABCMeta

    def __init__(self, dir_grid=None):
        """
        Initialize.

        :param dir_grid: (*str*) The directory of grid speciation data files.
        """
        self.dir_grid = dir_grid
        self.sector = None
        self.f = None

    @abstractmethod
    def get_spec_fn(self, sector):
        """
        Get grid speciation data file name.

        :param sector: (*Sector*) The sector.

        :return: (*str*) Grid speciation data file name.
        """
        pass

    @abstractmethod
    def get_spec_vars(self, sector, dims):
        """
        Get species variables.

        :param sector: (*Sector*) The sector.
        :param dims: (*list of Dimensions*) Dimension list.

        :return: (*list of variable*) Species variables.
        """
        pass

    @abstractmethod
    def read_spec(self, sector, spec_var):
        """
        Read species data.

        :param sector: (*Sector*) The sector.
        :param spec_var: (*Variable*) The species variable.

        :return: (*array*) Species data array.
        """
        pass

    @abstractmethod
    def get_spec_grid(self):
        """
        Get species grid.

        :return: (*GridDesc*) Species grid description.
        """
        pass
