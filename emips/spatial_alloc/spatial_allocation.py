from mipylib import geolib
import mipylib.numeric as np

__all__ = ['transform']


def transform(source, source_grid, dest_grid, method='auto'):
    """
    Spatial transform from source grid to destination grid.

    :param source: (*array*) Source data array.
    :param source_grid: (*GridDesc*) Source grid.
    :param dest_grid: (*GridDesc*) Destination grid.
    :param method: (*str*) Grid data assign method [auto | interp | inside]. Default is `auto`, interpolation
        method is used when destination grid resolution is higher than source grid, otherwise inside mean method
        is used.

    :return: (*array*) Destination data array.
    """
    if source_grid.proj == dest_grid.proj:
        if method == 'auto':
            method = 'interp' if source_grid.x_cell >= dest_grid.x_cell else 'inside'

        if method == 'interp':
            dest = np.interpolate.linint2(source_grid.x_coord, source_grid.y_coord, source, dest_grid.x_coord,
                                          dest_grid.y_coord)
        else:
            x, y = np.meshgrid(source_grid.x_coord, source_grid.y_coord)
            dest = np.interpolate.griddata((x, y), source, xi=(dest_grid.x_coord, dest_grid.y_coord),
                                           method='inside_mean')[0]
    else:
        dest = geolib.reproject(source, source_grid.x_coord, source_grid.y_coord, source_grid.proj,
                                dest_grid.x_coord, dest_grid.y_coord, dest_grid.proj)

    return dest
