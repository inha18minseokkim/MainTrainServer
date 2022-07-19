import Declaration
import DBManager
import requests
import json
import pydantic
from dependency_injector.providers import Singleton

class TradeManager:
    def __init__(self,_sessiondb,_serverdb):
        self.sessionDB = _sessiondb
        self.serverDB = _serverdb

    def getHash(self, apikey: str, secret: str, data: dict):  # api post 요청 시 사용 할 hash 함수
        # 단독으로 사용하지 마세요. 세션이 없다는 조건을 guard 하지 않음
        print('다음 정보를 hash', apikey, secret, data["CANO"], data["ACNT_PRDT_CD"])
        path = "uapi/hashkey"
        url = f"{Declaration.Base_URL}/{path}"
        headers = {
            "content-Type": 'application/json',
            "appKey": apikey,
            "appsecret": secret,
        }
        res = requests.post(url, headers=headers, data=json.dumps(data)).json()
        return res['HASH']

    def buyMarketPrice(self, useruuid: str, code: str, quantity: int):  # 현금 주식 매입 주문
        cursession = self.sessionDB.getSessionInfo(useruuid)
        print(useruuid,cursession)
        if cursession['code'] == 0:  # 현재 세션이 존재하지 않으면 0 리턴
            return {'code': 0}
        # httprequest 부분 시작
        data = {
            "CANO": cursession[DBManager.CANO],
            "ACNT_PRDT_CD": cursession[DBManager.ACNT],
            "PDNO": f"{code}",  # 종목코드
            "ORD_DVSN": "01",  # 시장가 코드
            "ORD_QTY": f"{quantity}",  # 수량
            "ORD_UNPR": "0",  # 가격은 시장가이므로 비워놔
        }
        h = self.getHash(cursession[DBManager.APIKEY], cursession[DBManager.SECRET], data)
        headers = {
            "content-type": 'application/json',
            "authorization": f"Bearer {cursession[DBManager.TOKEN]}",
            "appKey": cursession[DBManager.APIKEY],
            "appSecret": cursession[DBManager.SECRET],
            "tr_id": "VTTC0802U",
            "custtype": "P",
            "hashkey": h
        }
        print(h)
        print(cursession[DBManager.CANO], cursession[DBManager.ACNT], data['CANO'], data['ACNT_PRDT_CD'])
        path = "/uapi/domestic-stock/v1/trading/order-cash"
        url = f"{Declaration.Base_URL}/{path}"
        res = requests.post(url, headers=headers, data=json.dumps(data)).json()
        res['code'] = 1
        print(res)
        return res

    def sellMarketPrice(self, useruuid: str, code: str, quantity: int):  # 현금 주식 매도 주문
        cursession = self.sessionDB.getSessionInfo(useruuid)
        if cursession['code'] == 0:  # 현재 세션이 존재하지 않으면 0 리턴
            return {'code': 0}
        # httprequest 부분 시작
        data = {
            "CANO": cursession[DBManager.CANO],
            "ACNT_PRDT_CD": cursession[DBManager.ACNT],
            "PDNO": f"{code}",  # 종목코드
            "ORD_DVSN": "01",  # 시장가 코드
            "ORD_QTY": f"{quantity}",  # 수량
            "ORD_UNPR": "0",  # 가격은 시장가이므로 비워놔
        }
        h = self.getHash(cursession[DBManager.APIKEY], cursession[DBManager.SECRET], data)
        headers = {
            "content-type": 'application/json',
            "authorization": f"Bearer {cursession[DBManager.TOKEN]}",
            "appKey": cursession[DBManager.APIKEY],
            "appSecret": cursession[DBManager.SECRET],
            "tr_id": "VTTC0801U",
            "custtype": "P",
            "hashkey": h
        }
        print(h)
        print(cursession[DBManager.CANO], cursession[DBManager.ACNT], data['CANO'], data['ACNT_PRDT_CD'])
        path = "/uapi/domestic-stock/v1/trading/order-cash"
        url = f"{Declaration.Base_URL}/{path}"
        res = requests.post(url, headers=headers, data=json.dumps(data)).json()
        res['code'] = 1
        print(res)
        return res


if __name__ == "__main__":
    Declaration.initiate()
    container = DBManager.DBContainer()
    container2 = DBManager.DBContainer()
    sessiondb2 = container2.sessiondb_provider()
    serverdb: DBManager.ServerDBManager = container.serverdb_provider()
    sessiondb: DBManager.SessionDBManager = container.sessiondb_provider()
    tmpuuid = sessiondb.createSession('12181577','tokentoken',serverdb)[DBManager.UUID]
    print(sessiondb.getSessionInfo(tmpuuid))
    trader = TradeManager(container)
    print(trader.sessionDB.getSessionInfo(tmpuuid))
    print(trader.buyMarketPrice(tmpuuid,'005930',10))
    print(trader.buyMarketPrice(tmpuuid, '003550', 10))
    print(trader.buyMarketPrice(tmpuuid, '091170', 10))
    print(sessiondb2.getSessionInfo(tmpuuid))
    #print(sellMarketPrice('12181577','005930',1))
