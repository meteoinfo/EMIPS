import calendar

#Set types of pollutants
types = ['low','poi','pow','air']
def run(year, months, ddir):
    """
    Write the description file of the output binary data files.

    :param year: (*int*) Year.
    :param months: (*list*) List of months.
    :param ddir: (*string*) The directory where files is wrtied.
    """
    for month in months:
        tdir = os.path.join(ddir, str(year), '{}{:>02d}'.format(year, month))
        for tps in types:
            fn = os.path.join(tdir, 'emis_{}_{}_{}.ctl'.format(year,month,tps))
            print(fn)
            f = open(fn, 'w')
            f.write('dset ^emis_{}_{}_{}.grd\n'.format(year,month, tps))
            f.write('title model output from grapes\n')
            f.write('options sequential\n')
            f.write('undef -9.99E+33\n')
            f.write('xdef  751 linear   70.0000     0.1000\n')
            f.write('ydef  501 linear   15.0000     0.1000\n')
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