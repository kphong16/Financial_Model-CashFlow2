import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pandas.tseries.offsets import Day, MonthEnd
from datetime import datetime
from datetime import timedelta


def is_iterable(data):
    if type(data) == str:
        return False
    try:
        _ = iter(data)
        return True
    except TypeError:
        return False
        

def limited(val, lmt):
    tmp_val = val
    if is_iterable(lmt):
        for val_lmt in lmt:
            tmp_val = min(tmp_val, val_lmt)
    else:
        tmp_val = min(tmp_val, lmt)
    return tmp_val