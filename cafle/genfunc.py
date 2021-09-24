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
        

def limited(val, upper=None, lower=None):
    tmp_val = val
    
    if upper:
        if is_iterable(upper):
            for val_lmt in upper:
                tmp_val = min(tmp_val, val_lmt)
        else:
            tmp_val = min(tmp_val, upper)
    
    if lower:
        if is_iterable(lower):
            for val_lmt in lower:
                tmp_val = max(tmp_val, val_lmt)
        else:
            tmp_val = max(tmp_val, lower)
    return tmp_val
    
    
def rounding(val):
    tmprslt = val.fillna(0).applymap(lambda x: f"{x:,.0f}")
    return tmprslt