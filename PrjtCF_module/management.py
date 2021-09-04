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
        

# Calculate cash amount required and withdraw loan.
class wtdrw_mngmnt:
    def __init__(self, idxno, cstmng, acnt_oprtg):
        self.idxno = idxno
        self.cstmng = cstmng
        self.oprtg = acnt_oprtg
        
        self.amt_wtdrw = 0 # 인출된 금액
        self.rsdl_wtdrw = self.wtdrw_exptd # 인출필요금액(비용 등)
        
    @property
    def wtdrw_exptd(self):
        """총 지출필요금액을 확인한 후 운영계좌 잔액을 초과하는 금액
        (추가 인출이 필요한 금액)을 계산하여 반환"""
        cst_exptd = self.cstmng.ttl_exptd # 총 지출필요금액
        oprtg_bal = self.oprtg.bal_end[self.idxno] # 운영계좌 잔액
        
        amt_rqrd = max(cst_exptd - oprtg_bal, 0)
        # 지출필요금액에 대하여 운영계좌 잔액을 초과하는 금액 계산

        return amt_rqrd
    
    def wtdrw_equity(self, eqty):
        """equity instance에 대하여 idxno에 대응하는 인출예정금액(sub_scdd)을
        조회하여 운영계좌로 이체"""
        if eqty.is_wtdrbl:
            amt_wtdrw = eqty.ntnl.sub_scdd[self.idxno]
            eqty.ntnl.send(self.idxno, amt_wtdrw, self.oprtg)
            
    def wtdrw_loan(self, loan):
        """loan instance에 대하여 idxno에 대응하는 누적인출가능잔액 확인,
        누적인출가능잔액 내에서 인출필요금액(비용 등)을 운영계좌로 이체"""
        if loan.is_wtdrbl:
            ntnl_sub_rsdl = loan.ntnl.sub_rsdl_cum[self.idxno] # 누적인출가능잔액
            tmp_wtdrw = min(ntnl_sub_rsdl, self.rsdl_wtdrw)
            # 누적인출가능잔액과 인출필요금액을 비교하여 적은 금액을 대입
            
            loan.ntnl.send(self.idxno, tmp_wtdrw, self.oprtg)
            # 추가 인출필요금액을 운영계좌로 이체(누적인출가능잔액 내에서)
            
            self.amt_wtdrw += tmp_wtdrw # 인출된 금액
            self.rsdl_wtdrw -= tmp_wtdrw # 인출 후 잔여 인출필요금액
            