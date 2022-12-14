from typing import Optional
from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from loguru import logger
from pydantic import BaseModel
from dependencies import get_sesdb, get_serdb, get_scheduler
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

class Code(BaseModel):
    code: str

# 클라이언트에서 카카오 로그인 후 code 전송
@router.post('/auth')
async def kakaoAuth(item: Code, serdb = Depends(get_serdb), sesdb = Depends(get_sesdb)):

    auth_info = {}
    auth_info['access_token'] = item.code
    oauth = Oauth()
    user = oauth.userinfo("Bearer " + auth_info['access_token'])
    
    logger.debug(user)
    
    try:
        kakao_account = user["kakao_account"]
    except:
        return {'err' : '카카오 API 닉네임 정보수집 체크 안됨'}
    profile = kakao_account["profile"]
    name = profile["nickname"]
    id = str(user['id'])
    if "email" in kakao_account.keys():
        email = kakao_account["email"]
    else:
        email = f"{name}@kakao.com"

    user = serdb.getUserInfoFromServer(id) # db에서 id로 유저 검색해서 대입

    if user['code'] == 0: # 만약 회원가입이 안 된 유저라면
        # db 에 user 추가
        serdb.createAccount(id, name, apikey=Declaration.appKey, secret=Declaration.secret, cano='50067576', acnt='01', quantity=1000000)
    logger.debug(f'{id} 세션 만들기 시작')
    # 세션에 user 추가 로직 구현
    uid = sesdb.createSession(id, 'dummy', serdb)['uuid']

    # return {'uuid' : uid, 'registration' : user['code']^1, 'name': name}
    return {'uuid' : uid, 'registration': 0, 'name': name}