import threading

import pymongo as pymongo
import pymongo_inmemory

import Declaration
import uuid
import requests, json

from loguru import logger
from ast import literal_eval

#sessiondb : 세션을 유지하기 위해 사용하는 inmemory DB
#serverdb : 서버에 저장되어 있는 데이터들을 불러오는 db, mongodb atlas를 사용함
#inmemorydb는 껐다 키면 사라지니 세션 유지용으로만 사용!!
#dictionary key는 아래 값들을 명시적으로 사용 권장(오타 방지를 위해)
#데이터베이스 api를 호출 하면 항상 code를 체크해 주세요
#code가 0이면 뭔가가 안됐다는 것(db에 유저 정보가 없음)
KAKAOID = 'kakaoid'
SESSIONID = 'sessionid'
UUID = 'uuid'
LOGINTOKEN = 'logintoken'
NICKNAME = 'nickname'
APIKEY = 'apikey'
SECRET = 'secret'
QUANTITY = 'quantity'
MODEL = 'model'
TOKEN = 'token'
CANO = 'cano'
ACNT = 'acnt_prdt_cd'
STKLST = 'stocklist'
PERIOD = 'period'
FAVLST = 'favlist'

class ServerDBManager:
    def __init__(self):
        self.client = pymongo.MongoClient(  # 실제 배포에서는 아래거 써야됨.
            f"mongodb+srv://admin1:admin@cluster0.qbpab.mongodb.net/?retryWrites=true&w=majority")
        # client = pymongo.MongoClient(
        #     f"mongodb+srv://admin1:{Declaration.serverDBPW}@cluster0.qbpab.mongodb.net/?retryWrites=true&w=majority")
        self.serverdb = self.client.TradingDB
        logger.debug("serverdb 초기화 완료", self.serverdb)

    def createAccount(self, kakaoid: str, nickname: str, apikey: str, secret: str, cano: str, acnt: str, quantity=0):
        if self.getUserInfoFromServer(kakaoid)['code'] == 1:#서버에 해당 유저가 있으면 계정 생성 못함
            logger.debug(f"createAccount {kakaoid} 계정 정보가 이미 있으므로 계정생성 못함")
            return {'code':0, 'msg' : f'{kakaoid} 계정 정보가 이미 있으므로 계정생성 못함'}
        self.serverdb.user.insert_one(
            {KAKAOID: kakaoid, NICKNAME: nickname, APIKEY: apikey, SECRET: secret, QUANTITY: quantity
                , CANO: cano, ACNT: acnt, PERIOD : 20, FAVLST : ''})
        return {'code': 1}

    def createServerDummy(self):
        self.serverdb.user.insert_one({KAKAOID: '12181577', NICKNAME: '김민석', APIKEY: Declaration.appKey,
                                  SECRET: Declaration.secret, CANO: '50067576', ACNT: '01', QUANTITY: 1000000,
                                  STKLST: '{"005930":"0.5","003550":"0.3","091170":"0.2"}'})

    def getUserInfoFromServer(self, kakaoid: str):
        # {'_id': ObjectId('62c3ed0a991191142d3d56fc'), 'kakaoid': '12181577',
        # 'nickname': '김민석', 'apikey': 'asdf', 'secret': 'sec', 'quantity': 1000000, 'code': 1} ->kakaoid가 있을 경우
        # {'code': 0} -> kakaoid가 없을 경우
        cursor = self.serverdb.user.find({KAKAOID: kakaoid})
        res = list(cursor)
        if len(res) == 0:  # 정보가 없으면 0을 리턴
            logger.debug(f'{kakaoid} 에 해당하는 정보가 없음')
            return {'code': 0 ,'msg' :  f'{kakaoid} 에 해당하는 정보가 없음'}
        res = res[0]
        res['code'] = 1
        return res

    # 데이터 일관성 유지를 위해 세션단위에서만 정보 수정합니다. 이 함수는 단독으로 호출하지 마세요
    def editUserInfo(self, kakaoid: str, dic: dict):
        # dict = { NICKNAME : '바꿀 닉네임' } 으로 전달하면 해당 요소를 바꿈
        tmp = self.getUserInfoFromServer(kakaoid)
        res = tmp['code']
        if res == 0:
            logger.debug('editUserInfo : 해당 유저 찾을 수 없음', kakaoid)
            return {'code': 0 , 'msg' : f'{kakaoid} 해당 유저를 찾을 수 없음'}
        idquery = {KAKAOID: kakaoid}
        values = {"$set": dic}
        self.serverdb.user.update_one(idquery, values)
        return {'code': 1}

    def delUserInfo(self,kakaoid: str):
        # 회원탈퇴시 회원정보 삭제
        if self.getUserInfoFromServer(kakaoid)['code'] == 0:
            logger.debug(f'delUserInfo : {kakaoid} 해당 유저 찾을 수 없음', kakaoid)
            return {'code': 0 , 'msg' : f'{kakaoid} 해당 유저를 찾을 수 없음'}
        idquery = {KAKAOID: kakaoid}
        self.serverdb.user.delete_one(idquery)
        return {'code': 1}

    def getStockRatio(self, kakaoid: str):  # kakaoid유저가 설정해놓은 주가 비율을 가져옴
        cursor = self.serverdb.user.find({KAKAOID: kakaoid})
        res = list(cursor)
        if len(res) == 0:  # 정보가 없으면 0을 리턴
            return {'code': 0}
        try:
            tmp = res[0][STKLST]
        except:
            logger.debug('아직 비율이 설정되지 않음. 빈 리스트를 만듦')
            idquery = {KAKAOID : kakaoid}
            values = {"$set" : {STKLST : ''}}
            self.serverdb.user.update_one(idquery,values)
            return {}
        res = {k: float(v) for k, v in dict(literal_eval(res[0][STKLST])).items()}
        res['code'] = 1
        logger.debug('kakaoid에 대한 주가 비율 정보를 요청함', res)
        return res


    #User Collection이 아닌 scheduler collection
    def setScheduler(self, info: list[list[(str,int)]]): #Scheduler의 정보를 저장
        tlist: list[threading.Thread] = []
        for i in range(300):
            #logger.debug(i)
            idquery = {'idx' : i}
            values = {'$set' : {'value' : info[i]}}
            t = threading.Thread(target = self.serverdb.scheduler.update_one, args = (idquery,values))
            t.start()
            tlist.append(t)
        for t in tlist:
            t.join()
    def getScheduler(self): #Scheduler의 정보 가져옴
        cursor = self.serverdb.scheduler.find()
        res: list[list[(str, int)]] = list(cursor)
        return res
    def setSchedulerIdx(self, _idx):
        idquery = {'idx' : 'idx'}
        values = {'$set' : {'value' : _idx}}
        self.serverdb.scheduleridx.update_one(idquery,values)
        return
    def getSchedulerIdx(self):
        cursor = self.serverdb.scheduleridx.find({'idx' : 'idx'})
        return list(cursor)[0]['value']
    def getModelInfo(self):
        cursor: list[(str,float,float,str)] = list(self.serverdb.modelinfo.find())
        return cursor

class SessionDBManager:
    def __init__(self):
        self.client = pymongo_inmemory.MongoClient()
        self.sessiondb = self.client.sessionDB
        logger.debug("sessiondb 초기화 완료", self.sessiondb)

    def createDummyData(self):  # Unit test용 페이크 데이터 하나 만들어서 세션db에 넣음
        self.sessiondb.user.insert_one({KAKAOID: '12181577', SESSIONID: "1971301676", NICKNAME: '김민석', UUID:uuid.uuid4(),
                                   APIKEY: Declaration.appKey, SECRET: Declaration.secret,
                                   CANO: '50067576', ACNT: '01',
                                   TOKEN: Declaration.token, LOGINTOKEN: 'TMP',
                                   CANO: '50067576', ACNT: '01',
                                   QUANTITY: 1000000})
    def createSession(self, kakaoid: str, kakaotoken: str, serverdb: ServerDBManager):  # 서버에 있는 정보를 갖고 와서 세션을 만듬
        cursor = serverdb.getUserInfoFromServer(kakaoid)
        logger.debug(f'{kakaoid}에 대한 세션 생성')
        res = cursor
        if res['code'] == 0:  # 정보가 없으면 0을 리턴
            logger.debug(f"createSession: {kakaoid}에 대한 정보가 서버에 없음. 회원가입 먼저")
            return {'code': 0}
        res[UUID] = uuid.uuid4().hex
        del res['_id']

        headers = {"content-type": "application/json"}
        body = {"grant_type": "client_credentials",
                "appkey": res[APIKEY],
                "appsecret": res[SECRET]}
        path = "oauth2/tokenP"
        url = f"{Declaration.Base_URL}/{path}"
        logger.debug(f"{url}로 보안인증 키 요청")
        tokenres = requests.post(url, headers=headers, data=json.dumps(body)).json()
        res[TOKEN] = tokenres['access_token']
        logger.debug(f"token 생성 완료, 현재 계정 정보 {res[APIKEY]} {res[SECRET]} {kakaotoken} {res[TOKEN]} {res[UUID]}")

        res[LOGINTOKEN] = kakaotoken
        self.sessiondb.user.insert_one(res)
        logger.debug("세션생성 완료",res)
        logger.debug(res)
        return {'code': 1, UUID : res[UUID]}

    def isSessionAvailable(self,userUUID: uuid.UUID):  # api를 호출 하기 전 해당 세션이 있는지
        cursor = self.sessiondb.user.find({UUID: userUUID})
        res = list(cursor)
        # 카카오아이디를 파라미터로 받아서 현재 세션db에 존재하면 1, 존재하지않으면 0 리턴
        if len(res) == 0:
            return {'code': 0}
        else:
            return {'code': 1}

    def getSessionInfo(self, userUUID: uuid.UUID):  # 현재 세션에 대한 정보 리턴
        cursor = self.sessiondb.user.find({UUID: userUUID})
        res = list(cursor)
        if len(res) == 0:
            return {'code': 0}
        res = res[0]
        res['code'] = 1
        return res
    def getSessionKakaoId(self, userUUID: uuid.UUID):  # 현재 세션에 대한 정보 리턴
        cursor = self.sessiondb.user.find({UUID: userUUID})
        res = list(cursor)
        if len(res) == 0:
            return {'code': 0}
        res = res[0]
        return {'code': 1, 'res' : res[KAKAOID]}
    def editSession(self, userUUID: uuid.UUID, dic: dict, servermanager: ServerDBManager):
        # dict = { NICKNAME : '바꿀 닉네임' } 으로 전달하면 해당 요소를 바꿈
        ############################절대로 단독으로 실행하지 마세요###############################
        ############################서버DB에서 업데이트 후 자동으로 실행됨#########################
        ####################유저 정보를 수정하고싶으면 editUserInfo를 실행해 주세요#################
        logger.debug(f'{userUUID} 정보를 수정하려 함')
        tmp = self.getSessionInfo(userUUID)
        if tmp['code'] == 0:
            logger.debug('editUserInfo : 해당 유저 찾을 수 없음', userUUID)
            return {'code': 0}
        kakaoid = tmp[KAKAOID]
        idquery = {UUID: userUUID}
        logger.debug(f'{userUUID} 유효함 {kakaoid} 받아옴')
        values = {"$set": dic}
        self.sessiondb.user.update_one(idquery, values)
        servermanager.editUserInfo(kakaoid,dic)
        logger.debug("editSession: 수정 완료")
        return {'code': 1}







