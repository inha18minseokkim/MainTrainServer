import Declaration
import requests
def getStockInfo(code):
    #global appKey, secret, token, Base_URL
    print(f"{code}에 대한 주가 정보를 요청함")
    print(f"{Declaration.appKey} {Declaration.secret}")
    print(f"{Declaration.token}")
    headers = {
        "content-type": 'application/json',
        "authorization": f"Bearer {Declaration.token}",
        "appKey": Declaration.appKey,
        "appSecret": Declaration.secret,
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code" : "J",
        "fid_input_iscd": "005930",
    }
    path = "uapi/domestic-stock/v1/quotations/inquire-price"
    url = f"{Declaration.Base_URL}/{path}"
    res = requests.get(url,headers=headers,params=params).json()
    print(res)
    return res