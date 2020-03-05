from mipylib import geolib
import mipylib.numeric as np

__all__ = ['transform']

def transform(source, source_grid, dest_grid):
    """
    Spatial transform from source grid to destination grid.
    :param source: (*array*) Source data array.
    :param source_grid: (*GridDesc*) Source grid.
    :param dest_grid: (*GridDesc*) Destination grid.
    :return: (*array*) Destination data array.
    """
    if source_grid.proj == dest_grid.proj:
        dest = np.linint2(source_grid.x_coord, source_grid.y_coord, source, dest_grid.x_coord,
                          dest_grid.y_coord)
    else:
        dest = geolib.reproject(source, source_grid.x_coord, source_grid.y_coord, source_grid.proj,
                                dest_grid.x_coord, dest_grid.y_coord, dest_grid.proj)
    return dest
