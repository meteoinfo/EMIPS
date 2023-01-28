import mipylib.numeric as np
import inspect
import os
from .vertical_profile import VerticalProfile

__all__ = ['read_file']


def read_file(profile_fn, scc):
    """
    Read temporal profiles from profile files
    :param profile_fn: The profile file
    :param scc: Source classific code
    :return: Vertical profile
    """
    this_file = inspect.getfile(inspect.currentframe())
    current_path = os.path.abspath(os.path.dirname(this_file))
    vertical_profile = VerticalProfile()
    profile_f = open(os.path.join(current_path, os.pardir, "ge_data", profile_fn))
    line = profile_f.readline()
    while line:
        line = line.strip()
        if line == "/HEIGHT/":
            while True:
                line = profile_f.readline().split()
                if line == "/END/":
                    break
                if line[0] == scc:
                    line = [float(x) for x in line]
                    vertical_profile.weights = np.array(line[1:]).astype('float')
                    break
        line = profile_f.readline()
    profile_f.flush()
    profile_f.close()
    return vertical_profile
