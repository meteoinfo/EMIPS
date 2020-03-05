import mipylib.numeric as np
from .temporal_profile import TemporalProfile

class DiurnalProfile(TemporalProfile):

    def __init__(self, id="33", weights=None):
        """
        Diurnal profile
        :param id: The id.
        :param weights: The weights
        """
        super(DiurnalProfile, self).__init__(id, weights)

        if self.weights is None:
            self.weights = np.array([433,457,478,486,494,497,501,500,497,489,477,473,
                                466,440,397,352,324,300,288,284,292,316,354,403])
        elif isinstance(self.weights, (list, tuple)):
            self.weights = np.array(self.weights)
        self.weights = weights
