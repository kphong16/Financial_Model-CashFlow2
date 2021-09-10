import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pandas.tseries.offsets import Day, MonthEnd

from .genfunc import *

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
    """
    PARAMETERS
    - idxno : index
    - cstmng : cst_mngmnt instance
    - acnt_oprtg : operating account
    ATTRIBUTES
    - amt_wtdrw : amount withdrawed
    - rsdl_wtdrw : wtdrw_exptd amount which is calculated initially
    - wtdrw_exptd : cost amount which is expected to pay, over operating account balance end.
    METHODS
    - wtdrw_equity(equity) : equity instance, 
      + transfer sub-scheduled equity amount from equity instance to operating account
    - wtdrw_loan(loan_each) : each loan instance,
      + transfer sub-scheduled notional amount from loan instance to operating account
    """
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
        cst_exptd = self.cstmng.cst_ttl # 총 지출필요금액
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
            
    def wtdrw_loan(self, loan_each):
        """loan instance에 대하여 idxno에 대응하는 누적인출가능잔액 확인,
        누적인출가능잔액 내에서 인출필요금액(비용 등)을 운영계좌로 이체"""
        loan = loan_each
        if loan.is_wtdrbl:
            ntnl_sub_rsdl = loan.ntnl.sub_rsdl_cum[self.idxno] # 누적인출가능잔액
            tmp_wtdrw = min(ntnl_sub_rsdl, self.rsdl_wtdrw)
            # 누적인출가능잔액과 인출필요금액을 비교하여 적은 금액을 대입
            
            loan.ntnl.send(self.idxno, tmp_wtdrw, self.oprtg)
            # 추가 인출필요금액을 운영계좌로 이체(누적인출가능잔액 내에서)
            
            self.amt_wtdrw += tmp_wtdrw # 인출된 금액
            self.rsdl_wtdrw -= tmp_wtdrw # 인출 후 잔여 인출필요금액


# Calculate cost amount
class cst_mngmnt:
    """
    PARAMETERS
    - idxno : index
    - cost : cost account or account merged
    - loan : loan account or account merged
    ATTRIBUTES
    - cst_oprtg : total operating cost
    - cst_fnclfee : total financial fee amount
    - cst_fnclIR : total financial IR amount
    - cst_fncl : total financial fee amount and IR amount
    - cst_ttl = total operating and financial cost
    METHODS
    - pay_oprtcst(oprtg_account) : Pay each operating cost 
                from operating account to each cost account
    - pay_fnclcst(oprtg_account) : Pay each financial cost
                from operating account to each loan account
    """
    def __init__(self, idxno, cost, loan):
        self.idxno = idxno
        self.cost = cost
        self.loan = loan
        self._set_cst_oprtg()
        self._set_cst_loan()
        self._set_cst_ttl()
        
    def _set_cst_oprtg(self):
        # 해당 인덱스 기간 중 cost계좌 상 지출이 예정되어 있는 금액
        ttlsum = 0
        for key, val in self.cost.dct.items():
            val_scdd = val.add_scdd[self.idxno]
            setattr(self, key, val_scdd)
            ttlsum += val_scdd
        self.cst_oprtg = ttlsum
        
    def _set_cst_loan(self):
        # 해당 인덱스 기간 중 loan계좌 상 지출이 예정되어 있는 IR 및 fee
        ttlfee = 0
        ttlIR = 0
        for key, val in self.loan.dct.items():
            fee_scdd = val.fee.add_scdd[self.idxno]
            setattr(self, "fee_"+key, fee_scdd)
            ttlfee += fee_scdd
            
            IR_scdd = -val.ntnl.bal_strt[self.idxno] * val.IR.rate
            setattr(self, "IR_"+key, IR_scdd)
            ttlIR += IR_scdd
        self.cst_fnclfee = ttlfee
        self.cst_fnclIR = ttlIR
        self.cst_fncl = ttlfee + ttlIR
        
    def _set_cst_ttl(self):
        self.cst_ttl = self.cst_oprtg + self.cst_fncl
        
    def pay_oprtcst(self, oprtg):
        """운영계좌에서 운영비용(cost) 지출"""
        for key, acnt in self.cost.dct.items():
            oprtg.send(self.idxno, getattr(self, key), acnt)
            
    def pay_fnclcst(self, oprtg):
        """운영계좌에서 금융비용 지출"""
        for key, acnt in self.loan.dct.items():
            oprtg.send(self.idxno, getattr(self, "fee_"+key), acnt.fee)
            oprtg.send(self.idxno, getattr(self, "IR_"+key), acnt.IR)
            
            
# Calculate expected repayment of loan and repay loan.
class repay_mngmnt:
    """
    PARAMETERS
    - idxno
    - loan : each loan instance
    ATTRIBUTES
    - exptd_rpy_cum : cumulated residual notional amount which is expected to repay.
    - ntnl_bal_end : notional balance end
    - rpy_amt : amount which will be repayed
      + min(exptd_rpy_cum, ntnl_bal_end)
    METHODS
    - trsf_rpy(oprtg_account, repay_account):
      + transfer repayment amount from operating account to repayment account.
    - rpy_ntnl(repay_account):
      + transfer repayment amount from repayment account to each loan notional account.
    """
    def __init__(self, idxno, loan_each):
        self.idxno = idxno
        self.loan = loan_each
        
    # 상환요구금액 계산
    @property
    def amt_rpy_exptd(self):
        """상환 예정된 기일(만기 등)의 상환 예정 금액"""
        exptd_rpy_cum = max(self.loan.ntnl.add_rsdl_cum[self.idxno], 0)
        rpy_amt = min(exptd_rpy_cum, self.ntnl_bal_end)
        return rpy_amt
        
    @property
    def ntnl_bal_end(self):
        """미상환 대출원금 잔액"""
        return -self.loan.ntnl.bal_end[self.idxno]
        
    # Transfer repayment amount to repayment account
    def trsf_rpy(self, oprtg, rpyacc):
        amt_rpy = limited(self.amt_rpy_exptd, [oprtg.bal_end[self.idxno]])
        oprtg.send(self.idxno, amt_rpy, rpyacc)
    
    # Repay loan from repayment account
    def rpy_ntnl(self, rpyacc):
        amt_rpy = limited(rpyacc.bal_end[self.idxno], [self.ntnl_bal_end])
        rpyacc.send(self.idxno, amt_rpy, self.loan.ntnl)
        