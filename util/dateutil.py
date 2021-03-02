import time
import datetime

def format_datetime(datetime):
    try:
        fmt = '%Y-%m-%d %H:%M:%S'
        return datetime.strftime(fmt)
    except:
        return None


def format_date_normal(datetime):
    try:
        fmt = '%Y-%m-%d'
        return datetime.strftime(fmt)
    except:
        return None


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


"""
>>> n = datetime.strptime("2021-02-28", "%Y-%m-%d")
>>> datetime_offset_by_month(n, 1)
datetime.datetime(2021, 3, 31, 0, 0)
>>> n = datetime.strptime("2021-03-31", "%Y-%m-%d")
>>> datetime_offset_by_month(n, 1)
datetime.datetime(2021, 4, 30, 0, 0)
"""
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
'''
def secs2datestr(secs):
    if int(secs) < 0:
        return ""

    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(secs)))


def today():
    now = datetime.datetime.now()
    return datetime.datetime(year=now.year, month=now.month, day=now.day)
