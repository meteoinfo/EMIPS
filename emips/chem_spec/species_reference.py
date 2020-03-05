from .pollutant import Pollutant

class SpeciesReferenceItem(object):

    def __init__(self, scc, profile_id, pollutant):
        """
        Species reference item
        :param scc: Source classific code
        :param profile_id: Profile ID
        :param pollutant: The pollutant
        """
        self.scc = scc
        self.profile_id = profile_id
        if isinstance(pollutant, basestring):
            self.pollutant = Pollutant(pollutant)
        else:
            self.pollutant = pollutant

    def __eq__(self, other):
        """
        Equals another species reference item or not
        :param other: Another species reference item
        :return: Equals or not
        """
        if self.scc != other.scc:
            return False
        if self.pollutant != other.pollutant:
            return False
        if self.profile_id != other.profile_id:
            return False
        return True

    @classmethod
    def read_string(cls, line):
        """
        Read species reference item from string line
        :param line: The string line
        :return: Species reference item
        """
        data = line.split()
        scc = data[0]
        profile_id = data[1]
        name = data[2]
        if "!" in name:
            idx = name.index("!")
            name = name[:idx]

        pollutant = Pollutant(name)
        if pollutant.name == "VOC":
            pollutant = Pollutant("TOG")
        return SpeciesReferenceItem(scc, profile_id, pollutant)

class SpeciesReference(list):

    def __init__(self, spref_items=[]):
        """
        Species reference
        :param spref_items: Species reference items
        """
        list.__init__([])
        self.extend(spref_items)

    def contains(self, profile_id, pollutant):
        """
        Contains or not
        :param profile_id: The profile id
        :param pollutant: The pollutant
        :return: Contains or not
        """
        if isinstance(pollutant, basestring):
            pollutant = Pollutant(pollutant)
        for item in self:
            if item.profile_id == profile_id and item.pollutant == pollutant:
                return True
        return False