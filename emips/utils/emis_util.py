from .sector import SectorName
import calendar

__all__ = ['get_scc', 'get_month_days', 'get_year_days']

def get_scc(sector):
    """
    Get source classification code

    :param sector: The sector
    :return: Source classification code
    """
    scc = "10100101"
    if sector.name == SectorName.BIOMASS:
        scc = "28050001"
    elif sector.name == SectorName.ENERGY:
        scc = "10100101"
    elif sector.name == SectorName.INDUSTRY:
        scc = "30100101"
    elif sector.name == SectorName.RESIDENTIAL:
        scc = "28050002"
    elif sector.name == SectorName.WASTE_TREATMENT:
        scc = "28050001"
    elif sector.name in [SectorName.TRANSPORT, SectorName.AIR, SectorName.SHIPS]:
        scc = "22010000"
    elif sector.name == SectorName.AGRICULTURE:
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