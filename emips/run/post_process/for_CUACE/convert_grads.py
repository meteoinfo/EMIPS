import os
from mipylib import dataset
from mipylib import numeric as np
from emips.utils import SectorEnum

# Set emission low, poi, pow
emis_cuace = {}
emis_cuace['low'] = [SectorEnum.AGRICULTURE, SectorEnum.RESIDENTIAL,
                     SectorEnum.TRANSPORT, SectorEnum.SHIPS]
emis_cuace['poi'] = [SectorEnum.INDUSTRY]
emis_cuace['pow'] = [SectorEnum.ENERGY]
emis_cuace['air'] = [SectorEnum.AIR]

# Set time dimension of output file.
tn = 25  # 0 - 24 hour

def run(year, months, dir_in, dir_out, xn, yn, all_species):
    """
    Convert netcdf model-ready emission file to GrADS data 
    format for CUACE model.
    
    :param year: (*int*) Year.
    :param months: (*list*) List of months.
    :param dir_in: (*string*) The directory where netcdf data is stored.
    :param dir_out: (*string*) The directory where GrADS data is writed.
    :param xn: (*int*) x-dimension of output files.
    :param yn: (*int*) y-dimension of output files.
    """

    for month in months:
        print('**************')
        print('Month: {}'.format(month))
        print('**************')

        # Set directory for input and output files
        # dir_in = os.path.join(dir_in, str(year), '{}{:>02d}'.format(year, month))
        # dir_out = os.path.join(dir_out, str(year), '{}{:>02d}'.format(year, month))
        if not os.path.exists(dir_out):
            os.makedirs(dir_out)
        print('------------------Filepath------------------')
        print('dir_data: {}\ndir_out: {}'.format(dir_in, dir_out))
        # Loop
        for emis_type, sectors in emis_cuace.iteritems():
            print(emis_type, sectors)

            # set output binary dta file
            outfn = os.path.join(dir_out, 'emis_{}_{}_{}.grd'.format(year, month, emis_type))
            outer = dataset.bincreate(outfn)

            # Loop time number
            for t in range(tn):
                print('Time number: {}'.format(t))
                if t == tn - 1:
                    t = 0
                # Loop species
                for species in all_species:
                    data = None
                    # Loop sectors
                    for sector in sectors:
                        fn = os.path.join(dir_in, 'emis_{}_{}_{}_hour.nc'.format(sector.name, year, month))
                        if os.path.exists(fn):
                            f_in = dataset.addfile(fn)
                            if species.name in f_in.varnames:
                                dd = f_in[species.name][t]
                                if dd.sum() == 0:
                                    continue
                                if dd.contains_nan():
                                    dd[dd == np.nan] = 0
                                if data is None:
                                    data = dd
                                else:
                                    data = data + dd
                            f_in.close()
                        else:
                             print('Alarm! File not exists: {}'.format(fn))
                             continue
                    if data is None:
                        print('Is None: {}'.format(species))
                        data = np.zeros((yn, xn))
                    # Check the dimensions of the input and output files
                    if data.shape[0] != yn or data.shape[1] != xn:
                        print('The dimensions of input data and output data do not match!!!')
                        os.system("pause")

                    dataset.binwrite(outer, data.astype('float'), byteorder='little_endian', sequential=True)
            outer.close()
    print('#########################')
    print('Data convert completed!!!')
    print('#########################')

if __name__ == '__main__':
    import time
    import os
    from emips.chem_spec import RADM2
    time_start = time.time()

    # Settings
    year = 2017
    months = [1]
    dir_in = r'G:\test_gui\test_output'
    dir_out = os.path.join(dir_in, 'CUACE')
    xn = 502
    yn = 330
    all_species = RADM2().all_species()
    run(year, months, dir_in, dir_out, xn, yn, all_species)

    time_end = time.time()
    time = (time_end - time_start) / 60
    print('Time: {:.2f}min'.format(time))
