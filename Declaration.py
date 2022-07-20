import requests,json
from loguru import logger

appKey = "Not initiated"
secret = "Not initiated"

Base_URL = "https://openapivts.koreainvestment.com:29443"
token = "Not initiated"
serverDBPW = "Not initiated"
def initiate():
    global appKey,secret,token,serverDBPW
    # AppKey, Seccret 정보를 JSON에서 읽어서 Declaration 모듈에 저장
    logger.debug(f"시스템 시작")
    with open('secrets.json', 'r') as f:
        file = json.load(f)
        appKey = file['appKey']
        secret = file['secret']
        serverDBPW = file['serverDBPW']
        logger.debug(f"키 값 가져오기 성공 appkey : {appKey} secret : {secret}")
    # 키 가져왔으면 서버로부터 보안인증키 발급받아야 함
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": appKey,
            "appsecret": secret}
    path = "oauth2/tokenP"
    url = f"{Base_URL}/{path}"
    logger.debug(f"{url}로 보안인증 키 요청")
    res = requests.post(url, headers=headers, data=json.dumps(body)).json()
    token = res['access_token']
    logger.debug(f"token 생성 완료, 현재 계정 정보 {appKey} {secret} {token}")


def getHashTest(data): #api post 요청 시 사용 할 hash 함수 Test용
    path = "uapi/hashkey"
    url = f"{Base_URL}/{path}"
    headers = {
        "content-Type" : 'application/json',
        "appKey" : appKey,
        "appsecret" : secret,
    }
    res = requests.post(url,headers=headers,data=json.dumps(data)).json()
    return res['HASH']

