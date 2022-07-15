import pymongo as pymongo
import pymongo_inmemory
import Declaration
from ast import literal_eval
sessiondb = None
serverdb = None
#sessiondb : 세션을 유지하기 위해 사용하는 inmemory DB
#serverdb : 서버에 저장되어 있는 데이터들을 불러오는 db, mongodb atlas를 사용함
#inmemorydb는 껐다 키면 사라지니 세션 유지용으로만 사용!!
#dictionary key는 아래 값들을 명시적으로 사용 권장(오타 방지를 위해)
#데이터베이스 api를 호출 하면 항상 code를 체크해 주세요
#code가 0이면 뭔가가 안됐다는 것(db에 유저 정보가 없음)
KAKAOID = 'kakaoid'
SESSIONID = 'sessionid'
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
class ServerDBManager:
    def __init__(self):
        self.client = pymongo.MongoClient(  # 실제 배포에서는 아래거 써야됨.
            f"mongodb+srv://admin1:admin@cluster0.qbpab.mongodb.net/?retryWrites=true&w=majority")
        # client = pymongo.MongoClient(
        #     f"mongodb+srv://admin1:{Declaration.serverDBPW}@cluster0.qbpab.mongodb.net/?retryWrites=true&w=majority")
        self.serverdb = self.client.TradingDB
        print("serverdb 초기화 완료", serverdb)

    def createAccount(self, kakaoid, nickname, apikey, secret, cano, acnt, quantity=0):
        if self.getUserInfoFromServer(kakaoid)['code'] == 1:#서버에 해당 유저가 있으면 계정 생성 못함
            print("createAccount",kakaoid,"계정 정보가 이미 있으므로 계정생성 못함")
            return {'code':0}
        self.serverdb.user.insert_one(
            {KAKAOID: kakaoid, NICKNAME: nickname, APIKEY: apikey, SECRET: secret, QUANTITY: quantity
                , CANO: cano, ACNT: acnt})
        return {'code': 1}

    def createServerDummy(self):
        self.serverdb.user.insert_one({KAKAOID: '12181577', NICKNAME: '김민석', APIKEY: Declaration.appKey,
                                  SECRET: Declaration.secret, CANO: '50067576', ACNT: '01', QUANTITY: 1000000,
                                  STKLST: '{"005930":"0.5","003550":"0.3","091170":"0.2"}'})

    def getUserInfoFromServer(self, kakaoid):
        # {'_id': ObjectId('62c3ed0a991191142d3d56fc'), 'kakaoid': '12181577',
        # 'nickname': '김민석', 'apikey': 'asdf', 'secret': 'sec', 'quantity': 1000000, 'code': 1} ->kakaoid가 있을 경우
        # {'code': 0} -> kakaoid가 없을 경우
        cursor = self.serverdb.user.find({KAKAOID: kakaoid})
        res = list(cursor)
        if len(res) == 0:  # 정보가 없으면 0을 리턴
            return {'code': 0}
        res = res[0]
        res['code'] = 1
        return res

    def editUserInfo(self, kakaoid, dict, sessionmanager):
        # dict = { NICKNAME : '바꿀 닉네임' } 으로 전달하면 해당 요소를 바꿈
        res = self.getUserInfoFromServer(kakaoid)['code']
        if res == 0:
            print('editUserInfo : 해당 유저 찾을 수 없음', kakaoid)
            return {'code': 0}
        idquery = {KAKAOID: kakaoid}
        values = {"$set": dict}
        self.serverdb.user.update_one(idquery, values)
        sessionmanager.editSession(kakaoid, dict)
        return {'code': 1}

    def delUserInfo(self,kakaoid):
        # 회원탈퇴시 회원정보 삭제
        if self.getUserInfoFromServer(kakaoid)['code'] == 0:
            print('delUserInfo : 해당 유저 찾을 수 없음', kakaoid)
            return {'code': 0}
        idquery = {KAKAOID: kakaoid}
        self.serverdb.user.delete_one(idquery)
        return {'code': 1}

    def getStockRatio(self, kakaoid):  # kakaoid유저가 설정해놓은 주가 비율을 가져옴
        cursor = self.serverdb.user.find({KAKAOID: kakaoid})
        res = list(cursor)
        if len(res) == 0:  # 정보가 없으면 0을 리턴
            return {'code': 0}
        res = {k: float(v) for k, v in dict(literal_eval(res[0][STKLST])).items()}
        res['code'] = 1
        print('kakaoid에 대한 주가 비율 정보를 요청함', res)
        return res

class SessionDBManager:
    def __init__(self):
        self.client = pymongo_inmemory.MongoClient()
        self.sessiondb = self.client.sessionDB
        print("sessiondb 초기화 완료", self.sessiondb)

    def createDummyData(self):  # Unit test용 페이크 데이터 하나 만들어서 세션db에 넣음
        self.sessiondb.user.insert_one({KAKAOID: '12181577', SESSIONID: "1971301676", NICKNAME: '김민석',
                                   APIKEY: Declaration.appKey, SECRET: Declaration.secret,
                                   CANO: '50067576', ACNT: '01',
                                   TOKEN: Declaration.token, LOGINTOKEN: 'TMP',
                                   CANO: '50067576', ACNT: '01',
                                   QUANTITY: 1000000})
    def createSession(self, kakaoid, token, serverdb):  # 서버에 있는 정보를 갖고 와서 세션을 만듬
        cursor = serverdb.getUserInfoFromServer(kakaoid)
        print(kakaoid,'에 대한 세션 생성')
        res = cursor
        if res['code'] == 0:  # 정보가 없으면 0을 리턴
            print("createSession: ",kakaoid,"에 대한 정보가 서버에 없음. 회원가입 먼저")
            return {'code': 0}
        res[TOKEN] = token
        self.sessiondb.user.insert_one(res)
        print("세션생성 완료",res)
        return {'code': 1}

    def isSessionAvailable(self,kakaoid):  # api를 호출 하기 전 해당 세션이 있는지
        cursor = self.sessiondb.user.find({KAKAOID: kakaoid})
        res = list(cursor)
        # 카카오아이디를 파라미터로 받아서 현재 세션db에 존재하면 1, 존재하지않으면 0 리턴
        if len(res) == 0:
            return {'code': 0}
        else:
            return {'code': 1}

    def getSessionInfo(self, kakaoid):  # 현재 세션에 대한 정보 리턴
        cursor = self.sessiondb.user.find({KAKAOID: kakaoid})
        res = list(cursor)
        if len(res) == 0:
            return {'code': 0}
        res = res[0]
        res['code'] = 1
        return res
    # 데이터 일관성 유지를 위해 세션 수정은 없애고 서버에서만 사용하는걸로 하겠습니다. 이 함수는 쓰지마세요
    def editSession(self, kakaoid, dict):
        # dict = { NICKNAME : '바꿀 닉네임' } 으로 전달하면 해당 요소를 바꿈
        ############################절대로 단독으로 실행하지 마세요###############################
        ############################서버DB에서 업데이트 후 자동으로 실행됨#########################
        ####################유저 정보를 수정하고싶으면 editUserInfo를 실행해 주세요#################
        if self.getSessionInfo(kakaoid)['code'] == 0:
            print('editUserInfo : 해당 유저 찾을 수 없음', kakaoid)
            return {'code': 0}
        idquery = {KAKAOID: kakaoid}
        values = {"$set": dict}
        self.sessiondb.user.update_one(idquery, values)
        return {'code': 1}

if __name__ == "__main__":#Unit test를 위한 공간
    Declaration.initiate()

    serverdb = ServerDBManager()
    sessiondb = SessionDBManager()
    # serverdb.createServerDummy()
    # print(sessiondb.createSession('12181577','tokensample',serverdb))
    # print(sessiondb.createSession('1218157777','adsfasdfdas',serverdb))
    # print(sessiondb.editSession('12181577',{NICKNAME:'김민석석'}))
    # print(sessiondb.getSessionInfo('12181577'))

    # print(serverdb.createAccount('12171577','민석김','asdfasdf','asdfadsfcccc','00000000','01'))
    # print(serverdb.getUserInfoFromServer('12171577'))
    # print(serverdb.editUserInfo('12171577',{NICKNAME:'민석김김'},sessiondb))
    # print(serverdb.getUserInfoFromServer('12171577'))
    # print(serverdb.delUserInfo('12171577'))



