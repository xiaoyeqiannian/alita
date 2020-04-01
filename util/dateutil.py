#coding: utf-8

import time
import datetime
import locale

from contextlib import contextmanager

def date2string(dt, format="%Y-%m-%d %H:%M:%S"):
    return dt.strftime(format)

def date2week(dt):
    # 返回 （2107, 1, 1） 哪一年的 第几周 第几天
    return dt.isocalendar()

def date2weeknumber(a_dt):
    y = date2string(a_dt, "%Y")
    if int(a_dt.strftime("%W")) == 0:
        yes_y = int(y)-1
        t_dt = datetime.datetime.strptime("{0}-12-31".format(yes_y), "%Y-%m-%d")
        temp_week = t_dt.strftime("%W")

        return (yes_y, temp_week, 0)
    else:
        temp_week = a_dt.strftime("%W")
        return (y, temp_week, 0)


def string2date(dt_str, format="%Y-%m-%d %H:%M:%S"):
    """
    时间字符串转为时间
    :param dt_str:
    :param format:
    :return:
    """
    return datetime.datetime.strptime(dt_str, format)


def tms2date(tms):
    dateArray = datetime.datetime.utcfromtimestamp(tms)
    temp_date = dateArray + datetime.timedelta(hours=8)
    otherStyleTime = temp_date.strftime("%Y-%m-%d %H:%M:%S")
    return otherStyleTime

def date2tms(dt):
    """
    时间转为时间戳
    :param dt:
    :return:
    """
    return int(time.mktime(dt.timetuple()))


def datetime2date(dt):
    return datetime.date(dt.year, dt.month, dt.day)

def datetime2time(dt):
    return datetime.time(dt.hour, dt.minute, dt.second)

# 计算自然周第一天、自然月第一天和每天的凌晨时间戳
# t = time.time()
# print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_day_begin(t,1)))
# print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_week_begin(t,-2)))
# print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_month_begin(t,-3)))
def get_day_begin(ts = time.time(),N = 0):
    """
    N为0时获取时间戳ts当天的起始时间戳，N为负数时前数N天，N为正数是后数N天
    """
    return int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime(ts)),'%Y-%m-%d'))) + 86400*N

def get_week_begin(ts = time.time(),N = 0):
    """
    N为0时获取时间戳ts当周的开始时间戳，N为负数时前数N周，N为整数是后数N周，此函数将周一作为周的第一天
    """
    w = int(time.strftime('%w',time.localtime(ts)))
    if w == 0:
        w = 7
    return get_day_begin(int(ts - (w-1)*86400)) + N*604800

def get_month_begin(ts = time.time(),N = 0):
    """
    N为0时获取时间戳ts当月的开始时间戳，N为负数前数N月，N为正数后数N月
    """
    month_day = {1:31,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    cur_y,cur_m,cur_d = [int(x) for x in time.strftime('%Y-%m-%d',time.localtime(ts)).split('-')]
    if (cur_y%4 == 0 and cur_y%100 != 0) or cur_y%400 == 0:
        month_day[2] = 29
    else:
        month_day[2] = 28
    t = get_day_begin(ts) - (cur_d-1)*86400
    real_month = N + cur_m
    if real_month == cur_m:
        return t
    if N > 0:
        if real_month <= 12:
            for x in xrange(cur_m,real_month):
                t += month_day[x]*86400
        if real_month > 12:
            for x in xrange(cur_m,13):
                t += month_day[x]*86400
            t = get_month_begin(t,real_month - 13)
    if N < 0:
        if real_month >= 1:
            for x in xrange(real_month,cur_m):
                t -= month_day[x]*86400
        if real_month < 1:
            for x in xrange(1,cur_m):
                t -= month_day[x]*86400
            t -= month_day[12]*86400
            t = get_month_begin(t,real_month)
    return t

def datetime_offset_by_month(datetime1, n = 1):

    # create a shortcut object for one day
    one_day = datetime.timedelta(days = 1)

    # first use div and mod to determine year cycle
    q,r = divmod(datetime1.month + n, 12)

    # create a datetime2
    # to be the last day of the target month
    datetime2 = datetime.datetime(
        datetime1.year + q, r + 1, 1, datetime1.hour, datetime1.minute, datetime1.second) - one_day

    '''
       if input date is the last day of this month
       then the output date should also be the last
       day of the target month, although the day
       www.iplaypy.com
       may be different.
       for example:
       datetime1 = 8.31
       datetime2 = 9.30
    '''

    if datetime1.month != (datetime1 + one_day).month:
        return datetime2

    '''
        if datetime1 day is bigger than last day of
        target month, then, use datetime2
        for example:
        datetime1 = 10.31
        datetime2 = 11.30
    '''

    if datetime1.day >= datetime2.day:
        return datetime2

    '''
     then, here, we just replace datetime2's day
     with the same of datetime1, that's ok.
    '''

    return datetime2.replace(day = datetime1.day)

'''''
* datestr转换成secs
* 将时间字符串转化为秒("2012-07-20 00:00:00"->1342713600.0)
* @param datestr;
* @return secs;
*
'''
def datestr2secs(datestr):
    tmlist = []
    array = datestr.split(' ')
    array1 = array[0].split('-')
    array2 = array[1].split(':')
    for v in array1:
        tmlist.append(int(v))
    for v in array2:
        tmlist.append(int(v))
    tmlist.append(0)
    tmlist.append(0)
    tmlist.append(0)
    if len(tmlist) != 9:
        return 0
    return int(time.mktime(tmlist))


'''''
* secs转换成datestr
* 将秒转化为时间字符串(1342713600.0->"2012-07-20 00:00:00")
* @param secs;
* @return datestr;
*
'''
def secs2datestr(secs):
    if int(secs) < 0:
        return ""
    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(secs)))

@contextmanager
def use_locale(name):
    saved = locale.setlocale(locale.LC_ALL)
    try:
        yield locale.setlocale(locale.LC_ALL, name)
        # print 'good locale', name
    finally:
        locale.setlocale(locale.LC_ALL, saved)


def format(value):
    '''Jinja2 Template custom filter'''
    return friendly(value)

def friendly(dt, now=None):
    '''
    >>> now = datetime.datetime(2016, 10, 18, 13, 51)
    >>> type(now.strftime(u'%A %H:%M'))
    <type 'str'>
    >>> type(now.strftime('%A %H:%M'))
    <type 'str'>
    >>> now
    datetime.datetime(2016, 10, 18, 13, 51)
    >>> print friendly(datetime.datetime(2002, 10, 25), now)
    2002/10/25 00:00
    >>> print friendly(datetime.datetime(2016, 10, 16, 13, 51), now).encode('utf-8')
    星期日 13:51
    >>> print friendly(datetime.datetime(2016, 10, 15, 13, 51), now).encode('utf-8')
    星期六 13:51
    >>> print friendly(datetime.datetime(2016, 10, 23, 13, 51), now).encode('utf-8')
    星期日 13:51
    >>> print friendly(datetime.datetime(2016, 10, 24, 13, 51), now).encode('utf-8')
    星期一 13:51
    >>> print friendly(datetime.datetime(2016, 10, 18, 13, 51), now)
    13:51
    >>> print friendly(datetime.datetime(2016, 10, 18, 10), now)
    10:00
    >>> print friendly(datetime.datetime(2016, 10, 18, 11, 51), now)
    11:51
    >>> print friendly(datetime.datetime(2016, 10, 18, 14, 51, 20), now).encode('utf-8')
    星期二 14:51
    '''
    if now is None:
        now = datetime.datetime.now()
    delta = now - dt

    with use_locale('zh_CN.UTF-8'):
        if delta.days >= 7 or delta.days <= -7:
            # 年月日 时间
            return dt.strftime('%Y/%m/%d %H:%M')
        elif delta.days and -7 < delta.days < 7:
            # 星期几 时间
            fmt = u'%A %H:%M'.encode('utf-8')
            x = dt.strftime(fmt)
            return unicode(x, 'utf-8')
        else:
            return dt.strftime('%H:%M')

def now():
    dt = datetime.datetime.now()
    return dt


def today():
    now = datetime.datetime.now()
    when = datetime.datetime(year=now.year, month=now.month, day=now.day)
    return when


def getYearWeek(strdate):
    date = datetime.datetime.strptime(strdate, '%Y-%m-%d')
    YearWeek = date.isocalendar()
    return YearWeek

def getNowYearWeek():
    # 当前时间年第几周的计算
    timenow = datetime.datetime.now()
    NowYearWeek = timenow.isocalendar()
    return NowYearWeek

def getDayInweekMonday():
    week_num = datetime.datetime.now().weekday()
    Monday = datetime.datetime.now() + datetime.timedelta(days=-week_num)
    Monday = str(Monday)[0:10]
    return Monday

# weekflag格式为"2016#53"（即2016年第53周）
def getWeekFirstday(weekflag):
    year_str = weekflag[0:4]  # 取到年份
    week_str = weekflag[5:]  # 取到周
    if int(week_str)>=53:
        Monday = "Error,Week Num greater than 53!"
    else:
        yearstart_str = year_str + '0101'  # 当年第一天
        yearstart = datetime.datetime.strptime(yearstart_str, '%Y%m%d')  # 格式化为日期格式
        yearstartcalendarmsg = yearstart.isocalendar()  # 当年第一天的周信息
        yearstartweekday = yearstartcalendarmsg[2]
        yearstartyear = yearstartcalendarmsg[0]
        if yearstartyear < int(year_str):
            daydelat = (8 - int(yearstartweekday)) + (int(week_str) - 1) * 7
        else:
            daydelat = (8 - int(yearstartweekday)) + (int(week_str) - 2) * 7
        Monday = (yearstart + datetime.timedelta(days=daydelat)).date()
    return Monday
