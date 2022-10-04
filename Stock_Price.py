import Declaration
import requests
from loguru import logger
import FinanceDataReader as fdr
def getStockInfo(code):
    #global appKey, secret, token, Base_URL
    logger.debug(f"{code}에 대한 주가 정보를 요청함")
    logger.debug(f"{Declaration.appKey} {Declaration.secret}")
    logger.debug(f"{Declaration.token}")
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
    logger.debug(res)
    return res
def getStockCurPrice(code: str):
    df = fdr.DataReader(code)['Close']
    return int(df[-1])
if __name__ == "__main__":
    getStockCurPrice('005930')