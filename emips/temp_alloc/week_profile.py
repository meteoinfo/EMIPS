import mipylib.numeric as np
from .temporal_profile import TemporalProfile

class WeekProfile(TemporalProfile):

    def __init__(self, id="8", weights=None, weekday_weight=None, weekend_weight=None):
        """
        Month profile
        :param id: (*str*) The id.
        :param weights: (*array*) The weights. Start from Monday.
        :param weekday_weight: (*float*) The weekday weight.
        :param weekend_weight: (*float*) The weekend weight.
        """
        super(WeekProfile, self).__init__(id, weights)
        if self.weights is None:
            if weekday_weight is None or weekend_weight is None:
                weekday_weight = 147
                weekend_weight = 132
            self.weights = np.zeros(7)
            self.weights[:5] = weekday_weight
            self.weights[5:] = weekend_weight
        else:
            if isinstance(self.weights, (list, tuple)):
                self.weights = np.array(self.weights)

    @property
    def weekday_weight(self):
        """
        Weekday weight property
        :return: Weekday weight
        """
        return self.weights[:5].mean()

    @property
    def weekend_weight(self):
        """
        Weekend weight property
        :return: Weekend weight
        """
        return self.weights[5:].mean()