import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pandas.tseries.offsets import Day, MonthEnd
import datetime as dt
from datetime import datetime
from datetime import timedelta
from datetime import date
from functools import wraps

# import genfunc
# from index import Index
# from account import Account, Merge
from . import genfunc
from .index import Index, PrjtIndex
from .account import Account, Merge

__all__ = ['Loan']

class Loan(object):
    def __init__(self,
                 index = None, # basic index class
                 idxfn = None, # financial index class
                 amt_ntnl = None, # float
                 rate_fee = 0.0, # float
                 rate_IR = 0.0, # float
                 IRcycle = 1, # int, months
                 title = None, # string : "LoanA"
                 tag = None, # string tuple : ("tagA", "tagB")
                 note = "" # string
                 ):
        # index 입력
        if isinstance(index, Index):
            self.cindex = index
            self.index = index.index
        elif isinstance(index, PrjtIndex):
            self.cindex = index._prjt
            self.index = index.index
        
        # idxfn 입력
        if isinstance(idxfn, Index):
            self.cidxfn = idxfn
            self.idxfn = idxfn.index
        elif isinstance(index, PrjtIndex):
            self.cidxfn = idxfn._prjt
            self.idxfn = idxfn.index
            
        # 주요 변수 입력
        self.amt_ntnl = amt_ntnl
        self.rate_fee = rate_fee
        self.IRcycle = IRcycle
        self.rate_IR = rate_IR * self.IRcycle / 12
            
        # title 입력
        self.title = title
        
        # tag 입력 : tag는 튜플로 받음. string으로 입력된 경우 튜플로 변환 필요
        if isinstance(tag, tuple):
            self.tag = tag
        elif isinstance(tag, str):
            self.tag = tuple(tag)
        elif tag is None:
            self.tag = None
        else:
            raise ValueError("tag is not a tuple")
            
        # note 입력
        self.note = note
        
        # Account Setting
        self.ntnl = Account(self.cindex, self.title, self.tag)
        self.fee = Account(self.cindex, self.title, self.tag)
        self.IR = Account(self.cindex, self.title, self.tag)
        
        # Initialize
        self.dct = {}
        self._intlz()
        self.dctmrg = Merge(self.dct)
        
    def _intlz(self):
        # 초기화 함수 실행    
        self.ntnl.amt = self.amt_ntnl
        self.ntnl.subscdd(self.cidxfn.index[0], self.ntnl.amt)
        self.ntnl.addscdd(self.cidxfn.index[-1], self.ntnl.amt)
        self.dct['ntnl'] = self.ntnl
        
        self.fee.rate = self.rate_fee
        self.fee.amt = self.ntnl.amt * self.fee.rate
        self.fee.addscdd(self.cidxfn.index[0], self.fee.amt)
        self.dct['fee'] = self.fee
        
        self.IR.rate = self.rate_IR
        self.IR.amt = self.ntnl.amt * self.IR.rate
        self.IR.addscdd(self.cidxfn.index[1:], np.ones(len(self.cidxfn)) * self.IR.amt)
        self.dct['IR'] = self.IR
        
    @property
    def _df(self):
        return self.dctmrg._df
        
    @property
    def df(self):
        return self.dctmrg.df
    #####################################################
    # fee 입금 함수, IR 입금 함수, ntnl 출금, 입금 함수 추가 필요 #
        