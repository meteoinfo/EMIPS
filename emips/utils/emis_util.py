from .sector import SectorEnum
import calendar
from abc import ABCMeta, abstractmethod

__all__ = ['get_scc', 'get_month_days', 'get_year_days', 'EmissionReader']


def get_scc(sector):
    """
    Get source classification code

    :param sector: The sector
    :return: Source classification code
    """
    #    scc = "10100101"
    scc = None
    if sector == SectorEnum.BIOMASS:
        scc = "2810001000"
    elif sector == SectorEnum.ENERGY:
        scc = "10100101"
    elif sector == SectorEnum.INDUSTRY:
        scc = "30100101"
    elif sector == SectorEnum.RESIDENTIAL:
        scc = "2104001000"
    elif sector == SectorEnum.WASTE_TREATMENT:
        scc = "50100101"
    elif sector == SectorEnum.TRANSPORT:
        scc = "2294000000"
    elif sector == SectorEnum.AIR:
        scc = "2275000000"
    elif sector == SectorEnum.SHIPS:
        scc = "2280000000"
    elif sector == SectorEnum.AGRICULTURE:
        scc = "28050000"

    return scc


def get_year_days(year):
    """
    Get number of days in a year.
    :param year: (*int*) The year.
    :return: Number of days in a year.
    """
    return 366 if calendar.isleap(year) else 365


def get_month_days(year, month):
    """
    Get number of days in a month.
    :param year: The year.
    :param month: The month.
    :return:
    """
    return calendar.monthrange(year, month)[1]


class EmissionReader(object):

    __metaclass__ = ABCMeta

    def __init__(self, dir_emission=None):
        """
        Initialize.
        :param dir_emission: (*str*) Emission data directory
        :return:
        """
        self.dir_emission = dir_emission

    @abstractmethod
    def get_emis_fn(self, sector, pollutant, year, month):
        """
        Get emission data file name.

        :param sector: (*Sector*) The sector.
        :param pollutant: (*Pollutant*) The pollutant.
        :param year: (*int*) The year.
        :param month: (*int*) The month.

        :return: (*str*) Emission data file name.
        """
        pass

    @abstractmethod
    def read_emis(self, sector, pollutant, year, month):
        """
        Read emission gird data.

        :param sector: (*Sector*) The sector.
        :param pollutant: (*Pollutant*) The pollutant.
        :param year: (*int*) The year.
        :param month: (*int*) The month.

        :return: (*array*) Emission data array.
        """
        pass

    @abstractmethod
    def get_emis_grid(self):
        """
        Get emission grid.

        :return: (*GridDesc*) Emission grid description.
        """
        pass
