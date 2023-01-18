from ._mechanism import ChemicalMechanism
from .radm2 import RADM2
from .cb05_wrfchem import CB05_wrfchem
from .saprc99_wrfchem import SAPRC99_wrfchem
from .radm2_wrfchem import RADM2_wrfchem
from .mozart_wrfchem import MOZART_wrfchem
from .retro import RETRO
from mipylib.enum import Enum

__all__ = ['ChemMechEnum', 'ChemicalMechanism', 'RADM2', 'RETRO', 'CB05_wrfchem',
           'SAPRC99_wrfchem', 'RADM2_wrfchem', 'MOZART_wrfchem']


class ChemMechEnum(Enum):
    RADM2 = RADM2()
    CB05_wrfchem = CB05_wrfchem()
    SAPRC99_wrfchem = SAPRC99_wrfchem()
    RADM2_wrfchem = RADM2_wrfchem()
    MOZART_wrfchem = MOZART_wrfchem()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def nmvoc_species(self):
        return self.value.nmvoc_species()

    def voc_species(self):
        return self.value.voc_species()

    def all_species(self):
        return self.value.all_species()

    def species(self, name):
        return self.value.species(name)

    def lump_RETRO(self, spec, biomass=False):
        return self.value.lump_RETRO(spec, biomass)
