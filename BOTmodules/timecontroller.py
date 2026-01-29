from datetime import datetime

import pytz

APP_TIMEZONE = pytz.timezone('Europe/Moscow')

def today():
    return datetime.now(APP_TIMEZONE).date()

def now():
    return datetime.now(APP_TIMEZONE)