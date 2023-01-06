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
