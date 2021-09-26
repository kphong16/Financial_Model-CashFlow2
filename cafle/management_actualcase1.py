import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pandas.tseries.offsets import Day, MonthEnd

from .genfunc import *
from .index import *
from .account import *

__all__ = ['Intlz_sales_sellinlots', 'Intlz_costs', 'Intlz_accounts',
           'Mngmnt_sls', 'Mngmnt_wtdrw', 'Mngmnt_cst', 'Mngmnt_repay']
           

class Intlz_sales_sellinlots:
    def __init__(self,
                 index, # basic index class
                 idxsls = None, # financial index class
                 slsmtrx = None, # sales matrix
                 slsctrt = None, # sales contract schedule
                 slscsh = None, # sales cash schedule on each contract
                 ):
        # index 입력
        self.index = index
        if idxsls == None:
            idxsls = index
        self.idxsls = idxsls
        
        # 주요 변수 입력
        self.slsmtrx = slsmtrx
        self.prdtlst = list(self.slsmtrx.index)
        self.slsctrt = slsctrt
        self.slscsh = slscsh
        
        self.dct = {}
        self._intlz()
        
    def _intlz(self):
        for no, prdt in enumerate(self.prdtlst):
            tmp_acc = Account(self.index)
            self.dct[prdt] = tmp_acc
            setattr(self, prdt, tmp_acc)
            
            # input sales matrix data on account
            for colname in self.slsmtrx.columns:
                setattr(self.dct[prdt], colname, getattr(self.slsmtrx, colname)[prdt])
            
            # input sales contract, cash data on account
            setattr(self.dct[prdt], 'ctrt', self.slsctrt[prdt])
            setattr(self.dct[prdt], 'csh', self.slscsh)
            
        self.ttl = Merge(self.dct)
        for no, prdt in enumerate(self.prdtlst):
            setattr(self.ttl, prdt, self.dct[prdt])
            
            
# Setting Accounts
class Intlz_accounts:
    def __init__(self,
                 index, # index
                 accname, # list/str
                 ):
        self.index = index
        self.accname = accname
    
        self.dct = {}
        self._intlz()
    
    def __len__(self):
        return len(self.accname)
    
    def _intlz(self):
        for no, accname in enumerate(self.accname):
            tmp_acc = Account(self.index)
            self.dct[accname] = tmp_acc
            setattr(self, accname, tmp_acc)
            
        self.ttl = Merge(self.dct)
        for no, accname in enumerate(self.accname):
            setattr(self.ttl, accname, getattr(self, accname)