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
    """
    PARAMETERS
    - index : basic index class
    - idxfn : financial index class
    - amt_ntnl : notional amount, float
    - rate_fee : initial fee rate, float
    - rate_IR : interest rate, float
    - IRcycle : interest payment cycle(months), int
    - title : name of loan, str
    - tag : tags of loan, tuple of str
    - note : note, str
    ATTRIBUTES
    - cindex / cidxfn : index class instance
    - index / idxfn : index data of index class instance
    - is_wtdrbl : boolean(True or False), whether it's withdrawable or not.
                  default false
    - ntnl : Account instance of notional amount
    - fee : Account instance of fee amount
    - IR : Account instance of IR amount
    - dctmrg : Merge of dictionary ntnl, fee, IR.
    - _df : _df of dctmrg
    - df : df of dctmrg
    METHODS
    - set_wtdrbl_intldate(date) : If the date is an initial date, then set is_wtdrbl True
    - setback_wtdrbl_mtrt(date) : If the date is a maturity date, then set back is_wtdrbl False
    - set_wtdrbl_false() : set is_wtdrbl False
    """
    def __init__(self,
                 index = None, # basic index class
                 idxfn = None, # financial index class
                 amt_ntnl = 0, # float
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
        self.rate_IR = rate_IR
        self._rate_IR_cycle = rate_IR * self.IRcycle / 12
            
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
        
        # is withdrawable
        self._is_wtdrbl = False
        
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
        self.IR._rate_cycle = self._rate_IR_cycle
        self.IR.amt_cycle = self.ntnl.amt * self.IR._rate_cycle
        self.IR.addscdd(self.cidxfn.index[1:], np.ones(len(self.cidxfn)) * self.IR.amt_cycle)
        self.dct['IR'] = self.IR
        
    @property
    def _df(self):
        return self.dctmrg._df
        
    @property
    def df(self):
        return self.dctmrg.df
    
    #### set loan withdrawable ####
    @property
    def is_wtdrbl(self):
        return self._is_wtdrbl
    @is_wtdrbl.setter
    def is_wtdrbl(self, value):
        self._is_wtdrbl = value
    
    def set_wtdrbl_intldate(self, date):
        """If the date is an initial date, then set is_wtdrbl True"""
        if date == self.idxfn[0]:
            self.is_wtdrbl = True
    
    def setback_wtdrbl_mtrt(self, date):
        """If the date is a maturity date, then set back is_wtdrbl False"""
        if date == self.idxfn[-1]:
            self.set_wtdrbl_false()
            
    def set_wtdrbl_false(self):
        """Set is_wtdrbl False"""
        self.is_wtdrbl = False
    #### set loan withdrawable ####
    
    
    #####################################################
    # fee 입금 함수, IR 입금 함수, ntnl 출금, 입금 함수 추가 필요 #


class Merge_loan(Merge):
    @property
    def ntnl(self):
        tmp_dct = {key:val.ntnl for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return = rslt_acc
    
    @property
    def fee(self):
        tmp_dct = {key:val.fee for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc
        
    @property
    def IR(self):
        tmp_dct = {key:val.IR for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc