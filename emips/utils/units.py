from mipylib.enum import Enum

__all__ = ['Units', 'Weight', 'Area', 'Period']


class Unit(object):

    def __init__(self, name, ratio, name_abbr=None):
        """
        Initialization.
        :param name: (*str*) The name.
        :param ratio: (*float*) The ratio.
        :param name_abbr: (*str*) The name abbreviation. Default is `None` that the
            abbreviation is same as the name.
        """
        self.name = name
        self.ratio = ratio
        self.name_abbr = name if name_abbr is None else name_abbr

    def __str__(self):
        return "Name: {}; Ratio: {}; Abbr: {}".format(self.name, self.ratio, self.name_abbr)

    def __repr__(self):
        return self.__str__()

    def set_shrink(self, shrink):
        """
        Set shrink.
        :param shrink: (*float*) The shrink value.
        """
        self.ratio *= shrink


class Weight(Enum):
    G = Unit("G", 1., "g")  # Gram
    KG = Unit("KG", 1000., "kg")  # Kilogram
    MG = Unit("MG", 1.e6, "mg")  # Megagrams
    M = Unit("M", 1., "mole")  # Mole
    KM = Unit("KM", 1000., "k_mole")  # Kilo-moles
    MM = Unit("MM", 1.e6, "m_mole")  # Megamoles

    def is_mass(self):
        """
        Get whether the weight is mass.
        :return: (*bool*) Whether the weight is mass.
        """
        return self in [Weight.G, Weight.KG, Weight.MG]

    def is_mole(self):
        """
        Get whether the weight is mole.
        :return: (*bool*) Whether the weight is mole.
        """
        return self in [Weight.M, Weight.KM, Weight.MM]

    def convert_ratio(self, other):
        """
        Get convert ratio of the weight to the other weight.
        :param other: (*Weight*) The other weight.
        :return: (*float*) The convert ratio.
        """
        if self.is_mass() and other.is_mass():
            return self.value.ratio / other.value.ratio
        elif self.is_mass() and other.is_mole():
            return self.value.ratio / other.value.ratio
        else:
            return None


class Area(Enum):
    GRID = Unit("GRID", None)  # Grid area
    M2 = Unit("M2", 1., "m2")  # Square meter
    KM2 = Unit("KM2", 1.e6, "km2")  # Square kilometers

    def convert_ratio(self, other):
        """
        Get convert ratio of the weight to the other weight.
        :param other: (*Weight*) The other weight.
        :return: (*float*) The convert ratio.
        """
        return self.value.ratio / other.value.ratio


class Period(Enum):
    SECOND = Unit("SECOND", 1., "s")      # Second
    MINUTE = Unit("MINUTE", 60., "min")     # Minute
    HOUR = Unit("HOUR", 3600., "h")       # Hour
    DAY = Unit("DAY", 86400., "d")        # Day
    WEEK = Unit("WEEK", 604800., "w")     # Week
    MONTH = Unit("MONTH", 2592000., "m")  # Month with 30 days
    YEAR = Unit("YEAR", 31536000., "y")   # Year with 365 days

    @classmethod
    def of_month(cls, days=30):
        """
        Create Month period.
        :param days: (*int*) Days of the month.
        :return: (*Period*) Month period.
        """
        p = Period.MONTH
        p.set_shrink(days / 30.)
        return p

    @classmethod
    def of_year(cls, days=365):
        """
        Create year period.
        :param days: (*int*) Days of the year.
        :return: (*Period*) Year period.
        """
        p = Period.YEAR
        p.set_shrink(days / 365.)

    def convert_ratio(self, other):
        """
        Get convert ratio of the weight to the other weight.
        :param other: (*Weight*) The other weight.
        :return: (*float*) The convert ratio.
        """
        return self.value.ratio / other.value.ratio


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
        return "{}/{}/{}".format(self.weight.value.name_abbr, self.area.value.name_abbr,
                                 self.period.value.name_abbr)

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
        return self.weight.is_mole()

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

        # Weight
        wr = self.weight.convert_ratio(other.weight)
        if wr is None:
            return None

        # Area
        ar = self.area.convert_ratio(other.area)

        # Period
        if month_days != 30:
            if self.period == Period.MONTH:
                self.period.value.set_shrink(month_days / 30.)
            if other.period == Period.MONTH:
                other.period.value.set_shrink(month_days / 30.)

        if year_days != 365:
            if self.period == Period.YEAR:
                self.period.value.set_shrink(year_days / 365.)
            if other.period == Period.YEAR:
                other.period.value.set_shrink(year_days / 365.)

        pr = self.period.convert_ratio(other.period)

        return wr / ar / pr
