import threading

import AccountManager
import Declaration
import DBManager
import requests
import json
import pydantic
from loguru import logger
from dependency_injector.providers import Singleton

class TradeManager:
    def __init__(self):
        return
    def getHash(self, apikey: str, secret: str, data: dict):  # api post 요청 시 사용 할 hash 함수
        # 단독으로 사용하지 마세요. 세션이 없다는 조건을 guard 하지 않음
        logger.debug('다음 정보를 hash', apikey, secret, data["CANO"], data["ACNT_PRDT_CD"])
        path = "uapi/hashkey"
        url = f"{Declaration.Base_URL}/{path}"
        headers = {
            "content-Type": 'application/json',
            "appKey": apikey,
            "appsecret": secret,
        }
        res = requests.post(url, headers=headers, data=json.dumps(data)).json()
        return res['HASH']

    def buyMarketPrice(self, account: AccountManager.Account, code: str, quantity: int):  # 현금 주식 매입 주문
        if account.state == 0:
            return {'code' : 0 , 'msg' : 'account객체가 제대로 initiated 되지 않음'}
        logger.debug(account.kakaoid)
        # httprequest 부분 시작
        data = {
            "CANO": account.cano,
            "ACNT_PRDT_CD": account.acnt,
            "PDNO": f"{code}",  # 종목코드
            "ORD_DVSN": "01",  # 시장가 코드
            "ORD_QTY": f"{quantity}",  # 수량
            "ORD_UNPR": "0",  # 가격은 시장가이므로 비워놔
        }
        h = self.getHash(account.apikey, account.secret, data)
        headers = {
            "content-type": 'application/json',
            "authorization": f"Bearer {account.token}",
            "appKey": account.apikey,
            "appSecret": account.secret,
            "tr_id": "VTTC0802U",
            "custtype": "P",
            "hashkey": h
        }
        logger.debug(h)
        logger.debug(account.cano, account.acnt, data['CANO'], data['ACNT_PRDT_CD'])
        path = "/uapi/domestic-stock/v1/trading/order-cash"
        url = f"{Declaration.Base_URL}/{path}"
        res = requests.post(url, headers=headers, data=json.dumps(data)).json()
        res['code'] = 1
        logger.debug(res)
        return res

    def sellMarketPrice(self, account: AccountManager.Account, code: str, quantity: int):  # 현금 주식 매도 주문
        if account.state == 0:
            return {'code' : 0 , 'msg' : 'account객체가 제대로 initiated 되지 않음'}
        logger.debug(account.kakaoid)
        # httprequest 부분 시작
        data = {
            "CANO": account.cano,
            "ACNT_PRDT_CD": account.acnt,
            "PDNO": f"{code}",  # 종목코드
            "ORD_DVSN": "01",  # 시장가 코드
            "ORD_QTY": f"{quantity}",  # 수량
            "ORD_UNPR": "0",  # 가격은 시장가이므로 비워놔
        }
        h = self.getHash(account.apikey, account.secret, data)
        headers = {
            "content-type": 'application/json',
            "authorization": f"Bearer {account.token}",
            "appKey": account.apikey,
            "appSecret": account.secret,
            "tr_id": "VTTC0801U",
            "custtype": "P",
            "hashkey": h
        }
        logger.debug(h)
        logger.debug(account.cano, account.acnt, data['CANO'], data['ACNT_PRDT_CD'])
        path = "/uapi/domestic-stock/v1/trading/order-cash"
        url = f"{Declaration.Base_URL}/{path}"
        res = requests.post(url, headers=headers, data=json.dumps(data)).json()
        res['code'] = 1
        logger.debug(res)
        return res
    def isgoodbalance(self, account: AccountManager.Account): #리밸런싱 전 적절한 금액을 설정한 것인지 확인함
        res = 1 # 1은 가능 0은 불가능
        if account.state == 0:
            return {'code' : 0, 'msg' : 'Account 객체가 유효하지 않습니다.'}
        # 현재 포트폴리오에 이만큼 운용하세요 하고 설정해놓은 금액 값 -> self.quantity
        logger.debug(account.quantity)
        # 현재 유가평가금액총액 -> self.eval
        logger.debug(account.eval)
        # 현재 유가 비율 -> self.curaccount
        logger.debug(account.curaccount)
        # 설정된 유가 비율 -> self.ratio
        logger.debug(account.ratio)
        # 현재 설정해놓은 금액 self.quantity에 ratio를 곱해서 각 종목별로 얼마씩 투자해야되는지 확인 해야됨
        targetaccount = {k: int(v * account.quantity) for k, v in account.ratio.items()}
        del targetaccount['code']
        tmpaccount = {a['pdno']: int(a['pchs_amt']) for a in account.curaccount}
        logger.debug(tmpaccount)
        logger.debug(targetaccount)
        logger.debug(account.curpricedic)
        # 현재 잔고의 각 종목별 총액(현재가 x 주식수)를 구한다. ->self.curaccount의 pchs_amt를 사용
        buyrequest = []
        sellrequest = []
        for k, v in targetaccount.items():  # targetaccount -> 목표로 하는 잔고정보 tmpaccount -> 현재 가지고 있는 잔고정보
            diff = v - tmpaccount[k]
            curprice = account.curpricedic[k]  # 이거 가격 불러오는 모듈 구현해야됨
            if curprice * 100 > account.quantity: return {'code': 1, 'value': 0}
            if diff > 0:
                logger.debug(k, '를', diff, '만큼 더 사야됨')
                if diff // curprice == 0:
                    buyrequest.append([k, int(diff // curprice)])
            elif diff < 0:
                logger.debug(k, '를', diff, '만큼 팔아야됨')
                if diff // curprice == 0:
                    sellrequest.append([k, int(diff // curprice)])
        if len(buyrequest) != 0 or len(sellrequest) != 0 : return {'code' : 1, 'value': 0}

        #모든 검사를 통과해야만 1, 안정적인 자산운용이 가능하다는 신호를 줄 수 있다.
        return {'code': 1, 'value' : 1}

    def rebalance(self,account: AccountManager.Account):
        #현재 포트폴리오에 이만큼 운용하세요 하고 설정해놓은 금액 값 -> self.quantity
        logger.debug(account.quantity)
        #현재 유가평가금액총액 -> self.eval
        logger.debug(account.eval)
        #현재 유가 비율 -> self.curaccount
        logger.debug(account.curaccount)
        #설정된 유가 비율 -> self.ratio
        logger.debug(account.ratio)
        #현재 설정해놓은 금액 self.quantity에 ratio를 곱해서 각 종목별로 얼마씩 투자해야되는지 확인 해야됨
        targetaccount = { k:int(v*account.quantity) for k,v in account.ratio.items() }
        del targetaccount['code']
        tmpaccount = {a['pdno']:int(a['pchs_amt']) for a in account.curaccount}
        logger.debug(tmpaccount)
        logger.debug(targetaccount)
        logger.debug(account.curpricedic)
        #현재 잔고의 각 종목별 총액(현재가 x 주식수)를 구한다. ->self.curaccount의 pchs_amt를 사용
        buyrequest = []
        sellrequest = []
        for k,v in targetaccount.items(): #targetaccount -> 목표로 하는 잔고정보 tmpaccount -> 현재 가지고 있는 잔고정보
            diff = v-tmpaccount[k]
            curprice = account.curpricedic[k] #이거 가격 불러오는 모듈 구현해야됨
            if diff > 0:
                logger.debug(k,'를',diff,'만큼 더 사야됨')
                if diff//curprice != 0:
                    buyrequest.append([k,int(diff//curprice)])
            elif diff < 0:
                logger.debug(k,'를',diff,'만큼 팔아야됨')
                if diff//curprice != 0:
                    sellrequest.append([k,int(diff//curprice)])
        #이제 현재가격으로 나눈만큼 수량 주문하면됨
        threadlist = []
        for code,quantity in buyrequest:
            t = threading.Thread(target = self.buyMarketPrice,args = (account, code,quantity))
            threadlist.append(t)
            t.start()
        for code,quantity in sellrequest:
            t = threading.Thread(target = self.sellMarketPrice, args = (account, code,quantity))
            threadlist.append(t)
            t.start()
        for i in threadlist:
            i.join()

        return {'code' : 1}

if __name__ == "__main__":
    pass
    # Declaration.initiate()
    # container = Container.MainContainer()
    # container2 = Container.MainContainer()
    # serverdb: DBManager.ServerDBManager = container.serverdb_provider()
    # account: AccountManager.Account = AccountManager.Account('12181577',serverdb)
    # trader = TradeManager()
    # #logger.debug(trader.sessionDB.getSessionInfo('12181577'))
    # #logger.debug(trader.buyMarketPrice(account,'005930',10))
    # logger.debug(trader.sellMarketPrice(account, '003550', 10))
    # #logger.debug(trader.buyMarketPrice('12181577', '091170', 10))
    # #logger.debug(sessiondb2.getSessionInfo('12181577'))
    # # logger.debug(sellMarketPrice('12181577','005930',1))
