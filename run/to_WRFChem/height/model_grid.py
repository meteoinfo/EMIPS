#global 0.25
model_grid = GridDesc(proj, x_orig=0., x_cell=0.25, x_num=1440,
        y_orig=-89.75, y_cell=0.25, y_num=720)
#region 0.10
model_grid = GridDesc(proj, x_orig=70., x_cell=0.1, x_num=751,
    y_orig=15., y_cell=0.1, y_num=501)
#region 0.15
model_grid = GridDesc(proj, x_orig=70., x_cell=0.15, x_num=502,
    y_orig=15., y_cell=0.15, y_num=330)