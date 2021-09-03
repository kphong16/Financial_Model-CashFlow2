import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pandas.tseries.offsets import Day, MonthEnd


# receive sales amount
class sls_mngmnt:
    def __init__(self, idxno, sales):
        self.idxno = idxno
        self.sls = sales
        
        # 해당 인덱스 기간 중 인출 예정 sales amount
        self.sls_amt = 0
        
    # Check sales plan and input sales data
    def make_sls_plan(self):
        try:
            # check sales plan
            sls_amt = self.sls.sls_plan.loc[self.idxno]
            try:
                # input sales amount on this index no.
                self.sls.addamt(self.idxno, sls_amt)
                # input sales cash schedule on sales cash index.
                self.sls.subscdd(self.sls.csh_idx, sls_amt * self.sls.csh_rate)
            except AttributeError as err:
                print("AttributeError", err)
        except:
            pass
        
        self.sls_amt = self.sls.sub_rsdl_cum[self.idxno]
        
    # Receive sales amount on sales account
    def rcv_slsamt(self, acnt_sales):
        self.sls.send(self.idxno, self.sls_amt, acnt_sales)
        

