from mipylib.geolib import projinfo, gridarea
import mipylib.numeric as np


class GridDesc(object):

    def __init__(self, proj=projinfo(), x_coord=None, y_coord=None, x_orig=None, x_cell=None,
                 x_num=None, y_orig=None, y_cell=None, y_num=None):
        """
        Grid description.

        Using ``x_coord`` and ``y_coord`` or using ``x_orig``, ``x_cell``, ``x_num``,
        ``y_orig``, ``y_cell`` and ``y_num``.

        :param proj: (*ProjectionInfo*) The projection.
        :param x_coord: (*array*) X coordinate array.
        :param y_coord: (*array*) Y coordinate array.
        :param x_orig: (*float*) X coordinate at grid south-west corner.
        :param x_cell: (*float*) Grid spacing in x direction.
        :param x_num: (*int*) The number of grid cell in x direction.
        :param y_orig: (*float*) Y coordinate at grid.
        :param y_cell: (*float*) Grid spacing in y direction.
        :param y_num: (*int*) The number of grid cell in y direction.
        """
        self.proj = proj
        if x_coord is None:
            self.__x_orig = x_orig
            self.__x_cell = x_cell
            self.__x_num = x_num
            self.__y_orig = y_orig
            self.__y_cell = y_cell
            self.__y_num = y_num
            self.__x_coord = np.arange1(x_orig, x_num, x_cell)
            self.__y_coord = np.arange1(y_orig, y_num, y_cell)
        else:
            self.__x_coord = x_coord
            self.__y_coord = y_coord
            self.__x_orig = x_coord[0]
            self.__x_cell = x_coord[1] - x_coord[0]
            self.__x_num = len(x_coord)
            self.__y_orig = y_coord[0]
            self.__y_cell = y_coord[1] - y_coord[0]
            self.__y_num = len(y_coord)

    def __str__(self):
        r = 'Projection: %s' % self.proj
        r += '\nX origin: ' + str(self.__x_orig)
        r += '  X number: %i' % self.__x_num
        r += '  X cell: ' + str(self.__x_cell)
        r += '\nY origin: ' + str(self.__y_orig)
        r += '  Y number: %i' % self.__y_num
        r += '  Y cell: ' + str(self.__y_cell)
        return r

    __repr__ = __str__

    @property
    def x_coord(self):
        return self.__x_coord

    @property
    def y_coord(self):
        return self.__y_coord

    @property
    def x_orig(self):
        return self.__x_orig

    @property
    def x_cell(self):
        return self.__x_cell

    @property
    def x_num(self):
        return self.__x_num

    @property
    def x_end(self):
        return self.__x_coord[-1]

    @property
    def x_delta(self):
        return self.__x_coord[1] - self.__x_coord[0]

    @property
    def y_orig(self):
        return self.__y_orig

    @property
    def y_cell(self):
        return self.__y_cell

    @property
    def y_num(self):
        return self.__y_num

    @property
    def y_end(self):
        return self.__y_coord[-1]

    @property
    def y_delta(self):
        return self.__y_coord[1] - self.__y_coord[0]

    def get_x_value(self, v):
        """
        Find the nearest x coordinate value according to input value.
        :param v: (*float*) Input value.
        :return: (*float*) Found x coordinate value.
        """
        for x in self.__x_coord:
            if x >= v:
                return x
        return self.__x_coord[-1]

    def get_y_value(self, v):
        """
        Find the nearest y coordinate value according to input value.
        :param v: (*float*) Input value.
        :return: (*float*) Found y coordinate value.
        """
        for y in self.__y_coord:
            if y >= v:
                return y
        return self.__y_coord[-1]

    def grid_areas(self):
        """
        Calculate grid areas
        :return: (*array*) Grid areas
        """
        a = gridarea(self.__x_orig, self.__x_cell, self.__x_num, self.__y_orig, self.__y_cell,
                     self.__y_num, islonlat=self.proj.isLonLat(), allcell=False)
        return a
