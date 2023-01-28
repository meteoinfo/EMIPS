import utils
import temp_alloc
import spatial_alloc
import chem_spec
import vertical_alloc

__version__ = '1.0'

import os
ge_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ge_data')

version = 'EMIPS-1.0 (2022.08.04)'
__all__ = ['ge_data_dir', 'utils', 'temp_alloc', 'spatial_alloc', 'chem_spec', 'vertical_alloc', 'version']
