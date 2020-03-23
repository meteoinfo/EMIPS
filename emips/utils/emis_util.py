from .sector import SectorEnum
import calendar

__all__ = ['get_scc', 'get_month_days', 'get_year_days']

def get_scc(sector):
    """
    Get source classification code

    :param sector: The sector
    :return: Source classification code
    """
    scc = "10100101"
    if sector.name == SectorEnum.BIOMASS:
        scc = "2810001000"
    elif sector.name == SectorEnum.ENERGY:
        scc = "10100101"
    elif sector.name == SectorEnum.INDUSTRY:
        scc = "30100101"
    elif sector.name == SectorEnum.RESIDENTIAL:
        scc = "2104001000"
    elif sector.name == SectorEnum.WASTE_TREATMENT:
        scc = "50100101"
    elif sector.name == SectorEnum.TRANSPORT:
        scc = "2294000000"
    elif sector.name == SectorEnum.AIR:
        scc = "2275000000"
    elif sector.name == SectorEnum.SHIPS:
        scc = "2280000000"
    elif sector.name == SectorEnum.AGRICULTURE:
        scc = "28050000"

    return scc

def get_year_days(year):
    """
    Get number of days in a year.
    :param year: (*int*) The year.
    :return: Number of days in a year.
    """
    return 366 if calendar.isleep(year) else 365

def get_month_days(year, month):
    """
    Get number of days in a month.
    :param year: The year.
    :param month: The month.
    :return:
    """
    return calendar.monthrange(year, month)[1]