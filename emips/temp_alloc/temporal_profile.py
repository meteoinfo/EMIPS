
class TemporalProfile(object):

    def __init__(self, id=None, weights=None):
        """
        Month profile
        :param id: The id.
        :param weights: The weights
        """
        self.id = id
        self.weights = weights

    def __str__(self):
        r = self.__class__.__name__
        r += '\nWeights: {}'.format(self.weights)
        return r

    __repr__ = __str__

    def total_weight(self):
        """
        Get total weight.
        :return: Total weight.
        """
        return self.weights.sum()

    def get_weight(self, idx):
        """
        Get weight.
        :param idx: The index.
        :return: Weight
        """
        return self.weights[idx]

    def get_ratios(self):
        """
        Get weight ratios.
        :return: Weight ratios.
        """
        tw = float(self.total_weight())
        return self.weights / tw
	