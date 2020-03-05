from ._base import enum

__all__ = ['Units', 'Weight', 'Area', 'Period']

Weight = enum(G = "g",
              KG = "kg",
              MG = "mg",
              M = "mole",    #Mole
              KM = "kilo_mole",
              MM = "million_mole")

Area = enum(GRID = "grid",
            M2 = "m2",    #Squar meter
            KM2 = "km2")

Period = enum(SECOND = "s",
              MINUTE = "min",
              HOUR = "h",
              DAY = "d",
              WEEK = 'w',
              MONTH = "m",
              YEAR = "y")

class Units(object):

    def __init__(self, weight=Weight.KG, area=Area.M2, period=Period.SECOND):
        """
        Emission units.
        :param weight: (*Weight*) Weight.
        :param area: (*Area*) Area.
        :param period: (*Period*) Period.
        """
        self.weight = weight
        self.area = area
        self.period = period

    def __str__(self):
        return "%s/%s/%s" % (self.weight, self.area, self.period)

    __repr__ = __str__

    def __eq__(self, other):
        return self.weight == other.weight and \
               self.area == other.area and \
               self.period == other.period

    def is_mole(self):
        """
        Is mole weight or not
        :return: Mole or not
        """
        return self.weight in [Weight.M, Weight.KM, Weight.MM]

    def convert_ratio(self, other, month_days=30, year_days=365):
        """
        Get units convert ratio.
        :param other: (*Unit*) Another units.
        :param month_days: (*int*) Days of the month.
        :param year_days: (*int*) Days of the year.
        :return: Units convert ratio.
        """
        if self.area == Area.GRID or other.area == Area.GRID:
            return None

        wr = 1
        if self.weight != other.weight:
            if self.is_mole():
                if self.weight == Weight.M:
                    if other.weight == Weight.KM:
                        wr = 1e-3
                    elif other.weight == Weight.MM:
                        wr = 1e-6
                elif self.weight == Weight.KM:
                    if other.weight == Weight.M:
                        wr = 1e3
                    elif other.weight == Weight.MM:
                        wr = 1e-3
                elif self.weight == Weight.MM:
                    if other.weight == Weight.M:
                        wr = 1e-6
                    elif other.weight == Weight.KM:
                        wr = 1e-3
            else:
                if self.weight == Weight.G:
                    if other.weight == Weight.KG:
                        wr = 1e-3
                    elif other.weight == Weight.MG:
                        wr = 1e-6
                elif self.weight == Weight.KG:
                    if other.weight == Weight.G:
                        wr = 1e3
                    elif other.weight == Weight.MG:
                        wr = 1e-3
                elif self.weight == Weight.MG:
                    if other.weight == Weight.G:
                        wr = 1e-6
                    elif other.weight == Weight.KG:
                        wr = 1e-3

        #Area
        ar = 1
        if self.area == Area.M2:
            if other.area == Area.KM2:
                ar = 1e-6
        elif self.area == Area.KM2:
            if other.area == Area.M2:
                ar = 1e6

        #Period
        pr = 1
        if self.period == Period.SECOND:
            if other.period == Period.MINUTE:
                pr = 1. / 60.
            elif other.period == Period.HOURE:
                pr = 1. / 3600.
            elif other.period == Period.DAY:
                pr = 1. / 3600. / 24.
            elif other.period == Period.WEEK:
                pr = 1. / 3600. / 24. / 7.
            elif other.period == Period.MONTH:
                pr = 1. / 3600. / 24. / month_days
            elif other.period == Period.YEAR:
                pr = 1. / 3600. / 24. / year_days
        elif self.period == Period.MINUTE:
            if other.period == Period.SECOND:
                pr = 60.
            elif other.period == Period.HOURE:
                pr = 1. / 60.
            elif other.period == Period.DAY:
                pr = 1. / 60. / 24.
            elif other.period == Period.WEEK:
                pr = 1. / 60. / 24. / 7.
            elif other.period == Period.MONTH:
                pr = 1. / 60. / 24. / month_days
            elif other.period == Period.YEAR:
                pr = 1. / 60. / 24. / year_days
        elif self.period == Period.HOURE:
            if other.period == Period.SECOND:
                pr = 3600.
            elif other.period == Period.MINUTE:
                pr = 60.
            elif other.period == Period.DAY:
                pr = 1. / 24.
            elif other.period == Period.WEEK:
                pr = 1. / 24. / 7.
            elif other.period == Period.MONTH:
                pr = 1. / 24. / month_days
            elif other.period == Period.YEAR:
                pr = 1. / 24. / year_days
        elif self.period == Period.DAY:
            if other.period == Period.SECOND:
                pr = 3600. * 24.
            elif other.period == Period.MINUTE:
                pr = 60. * 24.
            elif other.period == Period.HOURE:
                pr = 24.
            elif other.period == Period.WEEK:
                pr = 1. / 7.
            elif other.period == Period.MONTH:
                pr = 1. / month_days
            elif other.period == Period.YEAR:
                pr = 1. / year_days
        elif self.period == Period.MONTH:
            if other.period == Period.SECOND:
                pr = 3600. * 24. * month_days
            elif other.period == Period.MINUTE:
                pr = 60. * 24. * month_days
            elif other.period == Period.HOURE:
                pr = 24. * month_days
            elif other.period == Period.DAY:
                pr = float(month_days)
            elif other.period == Period.WEEK:
                pr = month_days / 7.
            elif other.period == Period.YEAR:
                pr = float(month_days) / year_days

        elif self.period == Period.YEAR:
            if other.period == Period.SECOND:
                pr = 3600. * 24. * year_days
            elif other.period == Period.MINUTE:
                pr = 60. * 24. * year_days
            elif other.period == Period.HOURE:
                pr = 24. * year_days
            elif other.period == Period.DAY:
                pr = float(year_days)
            elif other.period == Period.WEEK:
                pr = year_days / 7.
            elif other.period == Period.MONTH:
                pr = float(year_days) / month_days

        return wr * ar * pr