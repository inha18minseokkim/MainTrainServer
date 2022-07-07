from typing import Optional
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from loguru import logger
import requests
router = APIRouter()

# 일단 임시로 카카오 api 키 받음
# 127.0.0.1:8000/kakao 로 접속하면 로그인 나옴
CLIENT_ID = 'fd9b44e80bfa7423f098d6ba45a87ee4'
CLIENT_SECRET = 'WYOkF2Y5YAaw21FLlSfcOgHK6NT0PNfj'
REDIRECT_URI = 'http://127.0.0.1:8000/auth'

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
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
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
    REST_API_KEY = "fd9b44e80bfa7423f098d6ba45a87ee4"
    REDIRECT_URI = "http://127.0.0.1:8000/auth"
    url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&response_type=code&redirect_uri={REDIRECT_URI}"
    response = RedirectResponse(url)
    return response

# 클라이언트에서 카카오 로그인 후 code 전송
@router.get('/auth')
async def kakaoAuth(response: Response, code: Optional[str]="NONE"):

    # 전달받은 authorization code를 통해서 access_token을 발급
    oauth = Oauth()
    auth_info = oauth.auth(code)

    # error 발생
    if "error" in auth_info:
        logger.debug("error")
        return JSONResponse(content={'message': 'authentication fail'}, status_code=404)

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

    '''
    id, name, (email) 사용하여 회원가입 and 인메모리 구현

    user = # db에서 id로 유저 검색해서 대입

    if user is None: # 만약 회원가입이 안 된 유저라면

        db에 user 추가 로직 구현
        
        1. db 에 user 추가

        # message = '회원가입이 완료되었습니다.'
        # value = {"status": 200, "result": "success", "msg": message}

    세션에 user 추가 로직 구현
    
    1.
    인메모리 db에 user 추가

    2.
    쿠키에 response.set_cookie(key="kakao", value=str(auth_info['access_token']))
    또는 response.set_cookie(key="kakao", value=uuid4())
    acess_token 을 세션키로 사용하게 되면 카카오 사용자 정보 요청 리퀘스트가 너무 많아짐
    따라서 랜덤 uuid 생성해서 세션키로 사용하는 것도 나쁘지 않음
    1. 세션 만료시간 정해야함
    2. 중복 로그인 괜찮은지 생각해 봐야함

    ##

    # message = '로그인에 성공하였습니다.'
    # value = {"status": 200, "result": "success", "msg": message}
    '''

    return {"login" : "success"}


# 나중에 Oauth 에 포함시켜야 할 함수
@router.get('/logout')
def kakaoLogout(request: Request, response: Response):

    url = "https://kapi.kakao.com/v1/user/unlink"
    KEY = request.cookies['kakao']
    headers = dict(Authorization=f"Bearer {KEY}")
    _res = requests.post(url,headers=headers)
    response.set_cookie(key="kakao", value=None)
    return {"logout": _res.json()}