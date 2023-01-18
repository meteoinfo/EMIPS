"""
# Author: Wencong Chen
# Date: 2022-11-27
# Purpose: Convert netcdf model-ready emission file to GrADS data format for CUACE model 
           and write the description file of the output binary data files.
"""
import convert_grads
import write_ctl
import time

dir_out = r'F:\run_data\emips\run_meic\test'


def run(run_config):
    """
    To CUACE model ready emission data files.

    :param run_config: (*RunConfigure*) The run configure.
    """
    time_start = time.time()

    year = run_config.emission_year
    months = [run_config.emission_month]
    dir_in = run_config.run_output_dir
    model_grid = run_config.spatial_model_grid
    xn = model_grid.x_num
    yn = model_grid.y_num
    xmin = model_grid.x_orig
    ymin = model_grid.y_orig
    xdelta = model_grid.x_cell
    ydelta = model_grid.y_cell

    print('Convert to grads...')
    convert_grads.run(year, months, dir_in, dir_out, xn, yn)

    print('Write .ctl files...')
    write_ctl.run(year, months, dir_out, xn, yn, xmin, ymin, xdelta, ydelta)

    print('-------------------')
    print('---All finished!---')
    print('-------------------')
    time_end = time.time()
    tt = (time_end - time_start) / 60
    print('Time: {:.2f}min'.format(tt))
