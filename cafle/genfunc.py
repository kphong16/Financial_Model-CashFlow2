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
    
    
def rounding(df):
    rslt_df = df.copy()
    for key, val in rslt_df.items():
        if all([isinstance(x, (int, float)) for x in rslt_df[key]]):
            if all([x < 100 for x in rslt_df[key]]):
                rslt_df[key] = rslt_df[key].fillna(0).apply(lambda x: f"{x:,.1f}")
            else:
                rslt_df[key] = rslt_df[key].fillna(0).apply(lambda x: f"{x:,.0f}")
    return rslt_df