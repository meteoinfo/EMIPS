from .month_profile import MonthProfile
from .week_profile import WeekProfile
from .diurnal_profile import DiurnalProfile
import re
import calendar
import datetime
import mipylib.numeric as np

__all__ = ['read_file', 'read_file_prof', 'month_allocation', 'week_allocation', 'diurnal_allocation',
           'month2hour', 'get_month_days', 'get_weekend_days', 'get_week_days']


def read_file(ref_fn, profile_fn, scc):
    """
    Read temporal profiles from reference and profile files
    :param ref_fn: The reference file
    :param profile_fn: The profile file
    :param scc: Source classific code
    :return: Species profile
    """
    # Read reference file
    n = len(scc)
    month_id = "462"
    week_id = "8"
    diurnal_id = "33"
    ref_f = open(ref_fn)
    for line in ref_f:
        line = line.strip()
        if len(line) < n:
            continue
        data = line.split()
        if data[0] == scc:
            month_id = data[1]
            week_id = data[2]
            diurnal_id = data[3]
            break
    ref_f.flush()
    ref_f.close()

    # Read profile file
    month_profile = MonthProfile()
    week_profile = WeekProfile()
    diurnal_profile = DiurnalProfile()
    diurnal_profile_weekend = DiurnalProfile()
    profile_f = open(profile_fn)
    line = profile_f.readline()
    while line:
        line = line.strip()
        if line == "/MONTHLY/":
            while True:
                line = profile_f.readline()
                if line.strip() == "/END/":
                    break
                if line[:5].strip() == month_id:
                    data = re.findall(r'.{4}', line[5:])
                    data = data[:12]
                    month_profile.weights = np.array(data).astype('int')
                    break
        if line == "/WEEKLY/":
            while True:
                line = profile_f.readline()
                if line.strip() == "/END/":
                    break
                if line[:5].strip() == week_id:
                    data = re.findall(r'.{4}', line[5:])
                    data = data[:7]
                    week_profile.weights = np.array(data).astype('int')
                    break
        if line == "/DIURNAL WEEKDAY/":
            while True:
                line = profile_f.readline()
                if line.strip() == "/END/":
                    break
                if line[:5].strip() == diurnal_id:
                    data = re.findall(r'.{4}', line[5:])
                    data = data[:24]
                    diurnal_profile.weights = np.array(data).astype('int')
                    break
        if line == "/DIURNAL WEEKEND/":
            while True:
                line = profile_f.readline()
                if line.strip() == "/END/":
                    break
                if line[:5].strip() == diurnal_id:
                    data = re.findall(r'.{4}', line[5:])
                    data = data[:24]
                    diurnal_profile_weekend.weights = np.array(data).astype('int')
                    break
        line = profile_f.readline()
    profile_f.flush()
    profile_f.close()
    return month_profile, week_profile, diurnal_profile, diurnal_profile_weekend


def read_file_prof(profile_fn, scc, ti=0, east=True):
    """
    Read temporal profiles from profile files
    :param profile_fn: The profile file
    :param scc: Source classific code
    :return: Species profile
    :param ti: Time zone
    :param east: Determine whether it is in the Eastern time zone, default is True
    """
    month_profile = MonthProfile()
    week_profile = WeekProfile()
    diurnal_profile = DiurnalProfile()
    profile_f = open(profile_fn)
    line = profile_f.readline()
    while line:
        line = line.strip()
        if line == "/MONTHLY/":
            while True:
                line = profile_f.readline().split()
                if line == "/END/":
                    break
                if line[0] == scc:
                    line = [float(x) for x in line]
                    month_profile.weights = np.array(line[1:]).astype('float')
                    break
        if line == "/WEEKLY/":
            while True:
                line = profile_f.readline().split()
                if line == "/END/":
                    break
                if line[0] == scc:
                    line = [float(x) for x in line]
                    week_profile.weights = np.array(line[1:]).astype('float')
                    break
        if line == "/HOURLY/":
            while True:
                line = profile_f.readline().split()
                if line == "/END/":
                    break
                if line[0] == scc:
                    line = [float(x) for x in line]
                    if ti == 0:
                        diurnal_profile.weights = np.array(line[1:]).astype('float')
                    else:
                        diurnal = np.array(line[1:]).astype('float')
                        if east is True:
                            cut1 = diurnal[0:ti]
                            cut2 = diurnal[ti:]
                        else:
                            cut1 = diurnal[0:len(diurnal) - ti]
                            cut2 = diurnal[len(diurnal) - ti:]
                        diurnal_profile.weights = cut2.join(cut1, 0)
                    break
        line = profile_f.readline()
    profile_f.flush()
    profile_f.close()
    return month_profile, week_profile, diurnal_profile


def month_allocation(data, month_profile):
    """
    Monthly allocation.

    :param data: Yearly emission data array - 2D.
    :param month_profile: Monthly profile.
    :return: Monthly emission data array - 3D.
    """
    ny, nx = data.shape
    m_data = np.zeros((12, ny, nx))
    weights = month_profile.get_ratios()
    for i in range(12):
        m_data[i] = data * weights[i]

    return m_data


def get_weekend_days(year, month):
    """
    Get number of weekend days in a month.

    :param year: (*int*) The year.
    :param month: (*int*) The month.
    :return: (*int*) Number of weekend days.
    """
    mdays = calendar.monthrange(year, month)[1]
    st = datetime.datetime(year, month, 1)
    et = datetime.datetime(year, month, mdays)
    n = 0
    while st <= et:
        if st.weekday() in [5, 6]:
            n += 1
        st = st + datetime.timedelta(days=1)
    return n


def get_week_days(year, month):
    """
    Get number of week days in a month.

    :param year: (*int*) The year.
    :param month: (*int*) The month.
    :return: (*array*) Number of week days. From Monday to Sunday.
    """
    mdays = calendar.monthrange(year, month)[1]
    st = datetime.datetime(year, month, 1)
    et = datetime.datetime(year, month, mdays)
    wdays = np.zeros(7, 'int')
    while st <= et:
        i = st.weekday()
        wdays[i] = wdays[i] + 1
        st = st + datetime.timedelta(days=1)
    return wdays


def week_allocation(data, week_profile, year, month, weekend_or_not=True):
    """
    Weekly allocation.

    :param data: (*array*) Monthly emission data array - 2D.
    :param week_profile: (*WeekProfile*) Weekly profile.
    :param year: (*int*) The year.
    :param month: (*int*) The month.
    :param weekend_or_not: (*bool*) Only use weekend or not for allocation.
    :return: (*array*) Daily emission data array in a week - 3D.
    """
    mdays = calendar.monthrange(year, month)[1]
    if weekend_or_not:
        weekend_days = get_weekend_days(year, month)
        weekday_days = mdays - weekend_days
        total_weight = week_profile.weekday_weight * weekday_days + week_profile.weekend_weight * \
                       weekend_days
        wdata = data / total_weight
        return wdata * week_profile.weekday_weight, wdata * week_profile.weekend_weight
    else:
        week_days = get_week_days(year, month)
        total_weight = (week_profile.weights * week_days).sum()
        wdata = data / total_weight
        ny, nx = data.shape
        d_data = np.zeros((7, ny, nx))
        for i in range(7):
            d_data[i] = wdata * week_profile.weights[i]

        return d_data


def diurnal_allocation(data, diurnal_profile):
    """
    Diurnal allocation.

    :param data: Daily emission data array - 2D.
    :param diurnal_profile: Diurnal profile.
    :return: Hourly emission data array - 3D.
    """
    ny, nx = data.shape
    h_data = np.zeros((24, ny, nx))
    weights = diurnal_profile.get_ratios()
    for i in range(24):
        h_data[i] = data * weights[i]

    return h_data


def month2hour(data, week_profile, diurnal_profile, year, month, weekend=False):
    """
    Allocated monthly emission data to hourly emission data

    :param data: Monthly emission data array - 2D.
    :param week_profile: Weekly profile.
    :param diurnal_profile: Diurnal profile.
    :param year: The year.
    :param month: The month.
    :param weekend: Is weekend or not.
    :return: Hourly emission data array - 3D.
    """
    w_data = month_allocation(data, week_profile, year, month)
    if weekend:
        d_data = diurnal_allocation(w_data[6], diurnal_profile)
    else:
        d_data = diurnal_allocation(w_data[0], diurnal_profile)
    return d_data


def get_month_days(year, month):
    """
    Get number of days in a month.

    :param year: The year.
    :param month: The month.
    :return: Month days
    """
    return calendar.monthrange(year, month)[1]
