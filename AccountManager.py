import Declaration
import DBManager
import requests,json
import Trader
import uuid
class Account:
    def __init__(self, sessionuuid: uuid.UUID):
        sessiondb = DBManager.DBContainer().sessiondb_provider()
        serverdb = DBManager.DBContainer().serverdb_provider()
        self.userinfo = sessiondb.getSessionInfo(sessionuuid)
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
        self.ratio = serverdb.getStockRatio(self.kakaoid)
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
            node = [column['pdno'],column['prdt_name'],column['hldg_qty'],column['pchs_avg_pric'],column['pchs_amt'],
                    column['prpr'],column['evlu_amt'],column['evlu_pfls_amt'],column['evlu_pfls_rt']]
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
        self.total = res2['tot_evlu_amt']  # 총평가금액
        self.deposit = res2['dnca_tot_amt']  # 예수금총금액
        self.eval = res2['scts_evlu_amt'] # 유가평가금액
        self.sumofprch = res2['pchs_amt_smtl_amt']  # 매입금액합계금액
        self.sumofern = res2['evlu_pfls_smtl_amt']  # 평가손익합계금액
        self.assticdc = res2['asst_icdc_amt']  # 자산증감액
        self.assticdcrt = res2['asst_icdc_erng_rt']  # 자산증감수익률





if __name__ == "__main__":
    Declaration.initiate()
    container = DBManager.DBContainer()
    container2 = DBManager.DBContainer()
    sessiondb2 = container2.sessiondb_provider()
    serverdb: DBManager.ServerDBManager = container.serverdb_provider()
    sessiondb: DBManager.SessionDBManager = container.sessiondb_provider()
    tmpuuid = sessiondb.createSession('12181577','tokentoken',serverdb)[DBManager.UUID]
    account = Account(tmpuuid)

