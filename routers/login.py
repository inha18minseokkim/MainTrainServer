from typing import Optional
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from loguru import logger
from Container import MainContainer
from pydantic import BaseModel
import requests
import Declaration
import uuid
router = APIRouter()

# 일단 임시로 카카오 api 키 받음
# 127.0.0.1:8000/kakao 로 접속하면 로그인 나옴
REST_API_KEY = '52750403fc68645f09dd49b6b777a752'
CLIENT_SECRET = 'L6MF44rcF2gbkthrCCoKpP7Q5Q9b6Jz4'
REDIRECT_URI = 'http://localhost:3000/signin'

class Oauth:

    def __init__(self):
        self.auth_server = "https://kauth.kakao.com%s"
        self.api_server = "https://kapi.kakao.com%s"
        self.default_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        }

    def auth(self, code):
        return requests.post(
            url=self.auth_server % "/oauth/token",
            headers=self.default_header,
            data={
                "grant_type": "authorization_code",
                "client_id": REST_API_KEY,
                # "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code,
            },
        ).json()
    
    def userinfo(self, bearer_token):
        return requests.post(
            url=self.api_server % "/v2/user/me",
            headers={
                **self.default_header,
                **{"Authorization": bearer_token}
            },
            # "property_keys":'["kakao_account.profile_image_url"]'
            data={}
        ).json()

# 아직 클라이언트가 없으므로 서버에서 로그인 페이지 생성
@router.get('/login')
def kakao():
    url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&response_type=code&redirect_uri={REDIRECT_URI}"
    response = RedirectResponse(url)
    return response

# 클라이언트에서 카카오 로그인 후 code 전송
@router.post('/auth')
async def kakaoAuth(request: Request):

    body = await request.json()
    # code = item.code
    code = body['code']
    # 전달받은 authorization code를 통해서 access_token을 발급
    oauth = Oauth()
    auth_info = oauth.auth(code)

    # error 발생
    if "error" in auth_info:
        logger.debug(auth_info)
        return JSONResponse(content={'message': 'authentication fail', **auth_info}, status_code=404)

    user = oauth.userinfo("Bearer " + auth_info['access_token'])
    '''
    user = {'id': 2328479814, 'connected_at': '2022-07-05T09:39:01Z', 'properties': {'nickname': '박성욱'},
            'kakao_account': {'profile_nickname_needs_agreement': False, 'profile': {'nickname': '박성욱'}}}
    '''
    logger.debug(user)
    
    kakao_account = user["kakao_account"]
    profile = kakao_account["profile"]
    name = profile["nickname"]
    id = user['id']
    if "email" in kakao_account.keys():
        email = kakao_account["email"]
    else:
        email = f"{name}@kakao.com"

    serverdb = MainContainer().serverdb_provider()
    sessiondb = MainContainer().sessiondb_provider()

    user = serverdb.getUserInfoFromServer(id) # db에서 id로 유저 검색해서 대입

    if user['code'] == 0: # 만약 회원가입이 안 된 유저라면
        # db 에 user 추가
        serverdb.createAccount(id, name, apikey=Declaration.appKey, secret=Declaration.secret, cano='50067576', acnt='01', quantity=1000000)

    # 세션에 user 추가 로직 구현
    uid = sessiondb.createSession(id, 'dummy', serverdb)['uuid']

    # return {'uuid' : uid, 'registration' : user['code']^1 }
    return {'uuid' : uid, 'registration': 1, 'name': name}

'''
@router.get('/logout')
def kakaoLogout(request: Request, response: Response):

    url = "https://kapi.kakao.com/v1/user/unlink"
    KEY = request.cookies['kakao']
    headers = dict(Authorization=f"Bearer {KEY}")
    _res = requests.post(url,headers=headers)
    response.set_cookie(key="kakao", value=None)
    return {"logout": _res.json()}
'''

class Item(BaseModel):
    apikey: str
    secret: str
    cano: int
    acnt: int
    quantity: int
    uuid: str

'''
005930 : 삼성전자
request body
{
    "interval": "YEAR",
    "code": "005930",
    "start": "2021"
}
'''
@router.post("/registration")
async def getChart(request: Request, item: Item):
    # logger.debug(item)
    logger.debug(request)
    body = await request.json()
    logger.debug(body)
    logger.debug(item)
    '''
    for i in request:
        logger.debug(i)
        logger.debug(request[i])'''
    
    # return item
    return item