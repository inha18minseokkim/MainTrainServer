import Declaration
import DBManager
import requests
def buyMarketPrice(kakaoid,code,quantity): #현금 주식 매입 주문
    cursession = DBManager.getSessionInfo(kakaoid)
    if cursession['code'] == 0: #현재 세션이 존재하지 않으면 0 리턴
        return {'code' : 0}
    #httprequest 부분 시작
    headers = {
        "content-type": 'application/json',
        "authorization": f"Bearer {cursession[DBManager.TOKEN]}",
        "appKey": cursession[DBManager.APIKEY],
        "appSecret": cursession[DBManager.SECRET],
        "tr_id": "VTTC0802U"
    }
    data = {
        "CANO": cursession[DBManager.CANO],
        "ACNT_PRDT_CD": cursession[DBManager.ACNT],
        "PDNO": f"{code}", #종목코드
        "ORD_DVSN": "01", #시장가 코드
        "ORD_QTY": f"{quantity}", #수량
        "ORD_UNPR": "0", #가격은 시장가이므로 비워놔
    }
    path = "/uapi/domestic-stock/v1/trading/order-cash"
    url = f"{Declaration.Base_URL}/{path}"
    res = requests.post(url, headers=headers, params=params).json()
    print(res)
    return res

def sellMarketPrice(kakaoid,code,quantity):
    cursession = DBManager.getSessionInfo(kakaoid)
    if cursession['code'] == 0:  # 현재 세션이 존재하지 않으면 0 리턴
        return {'code': 0}



if __name__ == "__main__":
    pass