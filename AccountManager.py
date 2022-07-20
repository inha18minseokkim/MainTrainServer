import Declaration
import DBManager
import logging
import requests,json
import Trader
import threading
import Container
import uuid
class Account:
    def __init__(self, sessionuuid: uuid.UUID, _sessiondb, _serverdb):
        self.sessiondb = _sessiondb
        self.serverdb = _serverdb
        self.userinfo = self.sessiondb.getSessionInfo(sessionuuid)
        print(self.userinfo)
        self.kakaoid = self.userinfo[DBManager.KAKAOID]
        self.nickname = self.userinfo[DBManager.NICKNAME]
        self.apikey = self.userinfo[DBManager.APIKEY]
        self.secret = self.userinfo[DBManager.SECRET]
        self.quantity = self.userinfo[DBManager.QUANTITY]
        self.token = self.userinfo[DBManager.TOKEN]
        self.cano = self.userinfo[DBManager.CANO]
        self.acnt = self.userinfo[DBManager.ACNT]
        #ratio는 내가 설정해놓은 비율
        self.ratio: dict = self.serverdb.getStockRatio(self.kakaoid)
        print(self.kakaoid)
        print(self.ratio)
        self.total = 0 #총평가금액
        self.deposit = 0 #예수금총금액
        self.eval = 0 #유가평가금액
        self.sumofprch = 0 #매입금액합계금액
        self.sumofern = 0 #평가손익합계금액
        self.assticdc = 0 #자산증감액
        self.assticdcrt = 0.0 #자산증감수익률
        self.curaccount: list = []
        self.getcurAccountInfo()
        print(self.curaccount)
        print(self.total,self.deposit,self.eval,self.sumofprch,self.sumofern,self.assticdc,self.assticdcrt)

    def getcurAccountInfo(self): #현재 내 잔고 현황 가져와서 딕셔너리 형태로
        #잔고 현황을 가져오는 것
        params = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt,
            "AFHR_FLPR_YN": "N", #시간외단일가:  ㄴㄴ 그냥 현재가로
            "OFL_YN": "N", #오프라인 여부
            "INQR_DVSN": "02", #조회구분 종목별
            "UNPR_DVSN": "01", #단가구분
            "FUND_STTL_ICLD_YN": "N", #펀드결제분 포함하지 않음
            "FNCG_AMT_AUTO_RDPT_YN": "N", #융자금액자동상환여부
            "PRCS_DVSN": "00", #전일매매포함
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        headers = {
            "content-type": 'application/json',
            "authorization": f"Bearer {self.token}",
            "appKey": self.apikey,
            "appSecret": self.secret,
            "tr_id": "VTTC8434R",
            "custtype": "P",
        }
        path = "/uapi/domestic-stock/v1/trading/inquire-balance"
        url = f"{Declaration.Base_URL}/{path}"
        res = requests.get(url, headers=headers, params=params).json()
        res1 = res['output1']
        res2 = res['output2'][0]
        print(res2)
        self.curaccount = []
        for column in res1:
            node = {'pdno': column['pdno'], 'prdt_name':column['prdt_name'], 'hldg_qty':int(column['hldg_qty']),'pchs_avg_pric':float(column['pchs_avg_pric']),
                    'pchs_amt' : int(column['pchs_amt']),
                    'prpr': int(column['prpr']), 'evlu_amt' : int(column['evlu_amt']),'evlu_pfls_amt': int(column['evlu_pfls_amt']),'evlu_pfls_rt': float(column['evlu_pfls_rt'])}
            self.curaccount.append(node)
        #pdno 종목코드
        #prdt_name 종목명
        #hldg_qty 보유수량
        #pchs_avg_pric 매입평균가격
        #pchs_amt 매입금액
        #prpr 현재가
        #evlu_amt 평가금액
        #evlu_pfls_amt 평가손익금액
        #evlu_pfls_rt 평가손익율
        self.total = int(res2['tot_evlu_amt'])  # 총평가금액
        self.deposit = int(res2['dnca_tot_amt'])  # 예수금총금액
        self.eval = int(res2['scts_evlu_amt']) # 유가평가금액
        self.sumofprch = int(res2['pchs_amt_smtl_amt'])  # 매입금액합계금액
        self.sumofern = int(res2['evlu_pfls_smtl_amt'])  # 평가손익합계금액
        self.assticdc = int(res2['asst_icdc_amt'])  # 자산증감액
        self.assticdcrt = float(res2['asst_icdc_erng_rt'])  # 자산증감수익률
    def rebalance(self, trader: Trader.TradeManager):
        #현재 포트폴리오에 이만큼 운용하세요 하고 설정해놓은 금액 값 -> self.quantity
        print(self.quantity)
        #현재 유가평가금액총액 -> self.eval
        print(self.eval)
        #현재 유가 비율 -> self.curaccount
        print(self.curaccount)
        #설정된 유가 비율 -> self.ratio
        print(self.ratio)
        #현재 설정해놓은 금액 self.quantity에 ratio를 곱해서 각 종목별로 얼마씩 투자해야되는지 확인 해야됨
        targetaccount = { k:int(v*self.quantity) for k,v in self.ratio.items() }
        del targetaccount['code']
        tmpaccount = {a['pdno']:int(a['pchs_amt']) for a in self.curaccount}
        print(tmpaccount)
        print(targetaccount)
        #현재 잔고의 각 종목별 총액(현재가 x 주식수)를 구한다. ->self.curaccount의 pchs_amt를 사용
        buyrequest = []
        sellrequest = []
        for k,v in targetaccount.items(): #targetaccount -> 목표로 하는 잔고정보 tmpaccount -> 현재 가지고 있는 잔고정보
            diff = v-tmpaccount[k]
            curprice = 30000 #이거 가격 불러오는 모듈 구현해야됨
            if diff > 0:
                print(k,'를',diff,'만큼 더 사야됨')
                buyrequest.append([k,int(diff//curprice)])
            elif diff < 0:
                print(print(k,'를',diff,'만큼 팔아야됨'))
                sellrequest.append([k,int(diff//curprice)])
        #이제 현재가격으로 나눈만큼 수량 주문하면됨
        threadlist = []
        for code,quantity in buyrequest:
            threadlist.append(trader.buyMarketPrice(code,quantity))
        for code,quantity in sellrequest:
            threadlist.append(trader.sellMarketPrice(code,quantity))
        for i in threadlist:
            i.join()

        return {'code' : 1}




if __name__ == "__main__":
    Declaration.initiate()
    container = DBManager.DBContainer()
    container2 = DBManager.DBContainer()
    sessiondb2 = container2.sessiondb_provider()
    serverdb: DBManager.ServerDBManager = container.serverdb_provider()
    sessiondb: DBManager.SessionDBManager = container.sessiondb_provider()
    tmpuuid = sessiondb.createSession('12181577','tokentoken',serverdb)[DBManager.UUID]
    account = Account(tmpuuid)

