import mipylib.numeric as np
from .temporal_profile import TemporalProfile

class MonthProfile(TemporalProfile):

    def __init__(self, id="462", weights=None):
        """
        Month profile
        :param id: The id.
        :param weights: The weights
        """
        super(MonthProfile, self).__init__(id, weights)

        if self.weights is None:
            self.weights = np.array([112,112,83,83,83,74,74,74,
                                     65,65,65,112])
        elif isinstance(self.weights, (list, tuple)):
            self.weights = np.array(self.weights)
