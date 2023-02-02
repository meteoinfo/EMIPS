import calendar
import os
from mipylib import miutil
import datetime

#Set types of pollutants
types = ['low','poi','pow','air']
def run(year, months, dir_out, xn, yn, xmin, ymin, xdelta, ydelta):
    """
    Write the description file of the output binary data files.

    :param year: (*int*) Year.
    :param months: (*list*) List of months.
    :param ddir: (*string*) The directory where files is wrtied.
    :param xn: (*int*) x-dimension of output files.
    :param yn: (*int*) y-dimension of output files.
    :param xmin: (*float*) The initial longitude of output files.
    :param ymin: (*float*) The initial latitude of output files.
    :param xdelta: (*float*) The spacing of longitudes of output files.
    :param ydelta: (*float*) The spacing of latitudes of output files.
    """
    for month in months:
        tdir = dir_out
        for tps in types:
            fn = os.path.join(tdir, 'emis_{}_{}_{}.ctl'.format(year,month,tps))
            print(fn)
            f = open(fn, 'w')
            f.write('dset ^emis_{}_{}_{}.grd\n'.format(year,month, tps))
            f.write('title model output from grapes\n')
            f.write('options sequential\n')
            f.write('undef -9.99E+33\n')
            f.write('xdef  {} linear   {:.2f}00     {:.2f}00\n'.format(xn, xmin, xdelta))
            f.write('ydef  {} linear   {:.2f}00     {:.2f}00\n'.format(yn, ymin, ydelta))
            f.write('zdef   1  linear 1 1\n')
            month_abbr = miutil.dateformat(datetime.datetime(year, month, 1), 'MMM', 'eng')
            month_abbr = month_abbr.upper()
            f.write('tdef   25 linear 00z01{}{}   60mn\n'.format(month_abbr, year))
            f.write('vars     32\n')
            f.write('  CO 1 99 Emission_CO (moles/m2/s)\n')
            f.write('  NO 1 99 Emission_NO (moles/m2/s)\n')
            f.write('  NO2 1 99 Emission_NO2 (moles/m2/s)\n')
            f.write('  ALD 1 99 Emission_ALD (moles/m2/s)\n')
            f.write('  CH4 1 99 Emission_CH4 (moles/m2/s)\n')
            f.write('  CSL 1 99 Emission_CSL (moles/m2/s)\n')
            f.write('  ETH 1 99 Emission_ETH (moles/m2/s)\n')
            f.write('  HC3 1 99 Emission_HC3 (moles/m2/s)\n')
            f.write('  HC5 1 99 Emission_HC5 (moles/m2/s)\n')
            f.write('  HC8 1 99 Emission_HC8 (moles/m2/s)\n')
            f.write('  HCHO 1 99 Emission_HCHO (moles/m2/s)\n')
            f.write('  ISOP 1 99 Emission_ISOP (moles/m2/s)\n')
            f.write('  KET 1 99 Emission_KET (moles/m2/s)\n')
            f.write('  NR 1 99 Emission_NR (g/m2/s)\n')
            f.write('  OL2 1 99 Emission_OL2 (moles/m2/s)\n')
            f.write('  OLE 1 99 Emission_OLE (g/m2/s)\n')
            f.write('  OLI 1 99 Emission_OLI (moles/m2/s)\n')
            f.write('  OLT 1 99 Emission_OLT (moles/m2/s)\n')
            f.write('  ORA2 1 99 Emission_ORA2 (moles/m2/s)\n')
            f.write('  PAR 1 99 Emission_PAR (g/m2/s)\n')
            f.write('  TERP 1 99 Emission_TERP (moles/m2/s)\n')
            f.write('  TOL 1 99 Emission_TOL (moles/m2/s)\n')
            f.write('  XYL 1 99 Emission_XYL (moles/m2/s)\n')
            f.write('  NH3 1 99 Emission_NH3 (moles/m2/s)\n')
            f.write('  SO2 1 99 Emission_SO2 (moles/m2/s)\n')
            f.write('  SULF 1 99 Emission_SULF (g/m2/s)\n')
            f.write('  PEC 1 99 Emission_PEC (g/m2/s)\n')
            f.write('  PMFINE 1 99 Emission_PMFINE (g/m2/s)\n')
            f.write('  PNO3 1 99 Emission_PNO3 (g/m2/s)\n')
            f.write('  POA 1 99 Emission_POA (g/m2/s)\n')
            f.write('  PSO4 1 99 Emission_PSO4 (g/m2/s)\n')
            f.write('  PMC 1 99 Emission_PMC (g/m2/s)\n')
            f.write('endvars')
            f.close()
    print('##########################')
    print('Write .ctl file completed!')
    print('##########################')

if __name__ == '__main__':  
    import time
    time_start = time.time()
    
    #Settings
    year = 2017
    months = [1]
    xn = 324
    yn = 180
    xmin = 64.0
    ymin = 15.0
    xdelta = 0.25
    ydelta = 0.25
    dir_out = r'G:\test'
    run(year, months, dir_out, xn, yn, xmin, ymin, xdelta, ydelta)
    
    time_end = time.time()
    time = (time_end - time_start) / 60
    print('Time: {:.2f}min'.format(time))