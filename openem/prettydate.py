# coding=utf8
from datetime import datetime, timedelta

# FIXME: replace this hack with proper gettext support
HEBREW = {
    'now' : u'רגע',
    'one minute' : u'דקה',
    'two minutes' : u'שתי דקות',
    '%d minutes' : u'%d דקות',
    'half an hour' : u'חצי שעה',
    'one hour' : u'שעה',
    'two hours' : u'שעתיים',
    '%d hours' : u'%d שעות',
    'one day' : u'יום',
    'two days' : u'יומיים',
    '%d days' : u'%d ימים',
    'one week' : u'שבוע',
    'two weeks' : u'שבועיים',
    '%d weeks' : u'%d שבועות',
    'one month' : u'חודש',
    'two months' : u'חודשיים',
    '%d months' : u'%d חודשים',
    'one year' : u'שנה',
    'two years' : u'שנתיים',
    '%d years' : u'%d שנים',
}

def prettydate(d, t=HEBREW.get):
    """
    >>> test = lambda (td): prettydate(datetime.utcnow() - td, t=lambda v:v).encode(u'utf8')

    >>> test(timedelta())
    'now'
    >>> test(timedelta(seconds=14))
    'now'
    >>> test(timedelta(seconds=15))
    'now'
    >>> test(timedelta(seconds=30))
    'now'
    >>> test(timedelta(seconds=31))
    'now'
    >>> test(timedelta(seconds=59))
    'now'
    >>> test(timedelta(seconds=60))
    'one minute'
    >>> test(timedelta(seconds=119))
    'one minute'
    >>> test(timedelta(minutes=1))
    'one minute'
    >>> test(timedelta(seconds=120))
    'two minutes'
    >>> test(timedelta(minutes=3))
    '3 minutes'
    >>> test(timedelta(minutes=10))
    '10 minutes'
    >>> test(timedelta(minutes=29))
    '29 minutes'
    >>> test(timedelta(minutes=30))
    'half an hour'
    >>> test(timedelta(minutes=39))
    'half an hour'
    >>> test(timedelta(minutes=40))
    'half an hour'
    >>> test(timedelta(minutes=59))
    'half an hour'
    >>> test(timedelta(minutes=60))
    'one hour'
    >>> test(timedelta(minutes=89))
    'one hour'
    >>> test(timedelta(minutes=90))
    'one hour'
    >>> test(timedelta(minutes=120))
    'two hours'
    >>> test(timedelta(minutes=60*3-1))
    'two hours'
    >>> test(timedelta(minutes=60*3))
    '3 hours'
    >>> test(timedelta(minutes=60*12))
    '12 hours'
    >>> test(timedelta(minutes=60*17))
    '17 hours'
    >>> test(timedelta(minutes=60*23))
    '23 hours'
    >>> test(timedelta(minutes=60*24))
    'one day'
    >>> test(timedelta(days=2))
    'two days'
    >>> test(timedelta(days=5))
    '5 days'
    >>> test(timedelta(days=7))
    'one week'
    >>> test(timedelta(days=13))
    'one week'
    >>> test(timedelta(days=14))
    'two weeks'
    >>> test(timedelta(days=20))
    'two weeks'
    >>> test(timedelta(days=21))
    '3 weeks'
    >>> test(timedelta(days=29))
    '4 weeks'
    >>> test(timedelta(days=30))
    'one month'
    >>> test(timedelta(days=59))
    'one month'
    >>> test(timedelta(days=60))
    'two months'
    >>> test(timedelta(days=30*3))
    '3 months'
    >>> test(timedelta(days=30*6))
    '6 months'
    >>> test(timedelta(days=30*12-1))
    '11 months'
    >>> test(timedelta(days=360))
    'one year'
    >>> test(timedelta(days=360*2))
    'two years'
    >>> test(timedelta(days=360*3-1))
    'two years'
    >>> test(timedelta(days=360*3))
    '3 years'
    >>> test(timedelta(days=360*120))
    '120 years'
    """   
    diff = (datetime.utcnow() - d).total_seconds()

    minute = 60
    hour = 60*minute
    day = 24*hour
    week = 7*day
    month = 30*day
    year = 360*day

    if diff < minute:
        return t('now')
    elif diff < 2*minute:
        return t('one minute')
    elif diff < 3*minute:
        return t('two minutes')
    elif diff < 30*minute:
        return t('%d minutes') % (diff / minute)
    elif diff < hour:
        return t('half an hour')
    elif diff < 2*hour:
        return t('one hour')
    elif diff < 3*hour:
        return t('two hours')
    elif diff < 24*hour:
        return t('%d hours') % (diff / hour)
    elif diff < 2*day:
        return t('one day')
    elif diff < 3*day:
        return t('two days')
    elif diff < week:
        return t('%d days') % (diff / day)
    elif diff < 2*week:
        return t('one week')
    elif diff < 3*week:
        return t('two weeks')
    elif diff < month:
        return t('%d weeks') % (diff / week)
    elif diff < 2*month:
        return t('one month')
    elif diff < 3*month:
        return t('two months')
    elif diff < 12*month:
        return t('%d months') % (diff / month)
    elif diff < 2*year:
        return t('one year')
    elif diff < 3*year:
        return t('two years')
    else:
        return t('%d years') % (diff / year)
