import pymongo as pymongo
import pymongo_inmemory
import Declaration
sessiondb = None
serverdb = None
#sessiondb : 세션을 유지하기 위해 사용하는 inmemory DB
#serverdb : 서버에 저장되어 있는 데이터들을 불러오는 db, mongodb atlas를 사용함
#inmemorydb는 껐다 키면 사라지니 세션 유지용으로만 사용!!
#dictionary key는 아래 값들을 명시적으로 사용 권장(오타 방지를 위해)
#데이터베이스 api를 호출 하면 항상 code를 체크해 주세요
#code가 0이면 뭔가가 안됐다는 것(db에 유저 정보가 없음)
KAKAOID = 'kakaoid'
NICKNAME = 'nickname'
APIKEY = 'apikey'
SECRET = 'secret'
QUANTITY = 'quantity'
MODEL = 'model'
TOKEN = 'token'
CANO = 'cano'
ACNT = 'acnt_prdt_cd'
def sessionDBinitiate(): #로컬 저장소에 있는 inmemory DB
    global sessiondb
    #세션을 저장하는 용도로만 사용
    # kakaoid : "카카오 아이디 String"
    # nickname : "사용자 닉네임 String"
    # apikey : "한국투자 apikey String"
    # secret : "한국투자 api secret String"
    # quantity : "현재 투자 설정 한 금액 Int"
    # token : "카카오에서 받은 토큰을 저장 String"
    # cano : "계좌번호 체계(8-2)의 앞 8자리, 종합계좌번호"
    # acnt : "계좌번호 체계(8-2)의 뒤 2자리, 계좌상품코드"
    # **저장되어있는 카카오아이디 -> 현재 세션 유지중, 저장안되어있음 -> 세션 없는것
    client = pymongo_inmemory.MongoClient()
    sessiondb = client.sessionDB
    print("sessiondb 초기화 완료",sessiondb)

def createDummyData(): #Unit test용 페이크 데이터 하나 만들어서 세션db에 넣음
    global sessiondb
    sessiondb.user.insert_one({KAKAOID:'12181577',NICKNAME:'김민석',APIKEY:'asdf',SECRET:'sec', CANO : '50067576', ACNT : '01', QUANTITY: 1000000})

def createSession(kakaoid,token): #서버에 있는 정보를 갖고 와서 세션을 만듬
    global sessiondb,serverdb
    cursor = serverdb.user.find({KAKAOID: kakaoid})
    res = list(cursor)
    if len(res) == 0:  # 정보가 없으면 0을 리턴
        return {'code': 0}
    res = res[0]
    res[TOKEN] = token
    sessiondb.user.insert_one(res)
    return {'code' : 1}
def isSessionAvailable(kakaoid): #api를 호출 하기 전 해당 세션이 있는지
    global sessiondb
    cursor = sessiondb.user.find({KAKAOID: kakaoid})
    res = list(cursor)
    #카카오아이디를 파라미터로 받아서 현재 세션db에 존재하면 1, 존재하지않으면 0 리턴
    if len(res) == 0: return {'code' : 0}
    else: return  {'code' : 1}

def getSessionInfo(kakaoid):#현재 세션에 대한 정보 리턴
    global sessiondb
    cursor = sessiondb.user.find({KAKAOID: kakaoid})
    res = list(cursor)
    if len(res) == 0:
        return {'code' : 0}
    res = res[0]
    res['code'] = 1
    return res
def editSession(kakaoid,dict):
    # dict = { NICKNAME : '바꿀 닉네임' } 으로 전달하면 해당 요소를 바꿈
    ############################절대로 단독으로 실행하지 마세요###############################
    ############################서버DB에서 업데이트 후 자동으로 실행됨#########################
    ####################유저 정보를 수정하고싶으면 editUserInfo를 실행해 주세요#################
    global sessiondb
    if getSessionInfo(kakaoid)['code'] == 0:
        print('editUserInfo : 해당 유저 찾을 수 없음', kakaoid)
        return {'code': 0}
    idquery = {KAKAOID: kakaoid}
    values = {"$set": dict}
    sessiondb.user.update_one(idquery, values)
    return {'code': 1}


def serverDBinitiate():
    global serverdb
    # db서버에서 클라이언트 불러옴 db변수를 통해 클라이언트에 접근 ㄱㄱ
    # DB에 들어가는 element set (JSON형식으로 관리 되기 때문에 변수 혼동 유의 ex) nickname 인데 nicname 이런식으로 오타나면 골치아픔)
    # kakaoid : "카카오 아이디 String"
    # nickname : "사용자 닉네임 String"
    # apikey : "한국투자 apikey String"
    # secret : "한국투자 api secret String"
    # quantity : "현재 투자 설정 한 금액 Int"
    # model : "투자한 모델 파일 경로/이름 "
    client = pymongo.MongoClient( #실제 배포에서는 아래거 써야됨.
        f"mongodb+srv://admin1:admin@cluster0.qbpab.mongodb.net/?retryWrites=true&w=majority")
    # client = pymongo.MongoClient(
    #     f"mongodb+srv://admin1:{Declaration.serverDBPW}@cluster0.qbpab.mongodb.net/?retryWrites=true&w=majority")
    serverdb = client.TradingDB
    print("serverdb 초기화 완료",serverdb)

    #서버의 계정 생성
def createAccount(nickname,apikey,secret):
    global serverdb
    serverdb.user.insert_one({KAKAOID: '12181577', NICKNAME: '김민석', APIKEY: 'asdf', SECRET: 'sec', QUANTITY: 0})

def createServerDummy():
    global serverdb
    serverdb.user.insert_one({KAKAOID: '12181577', NICKNAME: '김민석', APIKEY: Declaration.appKey, SECRET: Declaration.secret, CANO : '50067576', ACNT : '01', QUANTITY: 1000000})


def getUserInfoFromServer(kakaoid):
    # {'_id': ObjectId('62c3ed0a991191142d3d56fc'), 'kakaoid': '12181577',
    # 'nickname': '김민석', 'apikey': 'asdf', 'secret': 'sec', 'quantity': 1000000, 'code': 1} ->kakaoid가 있을 경우
    # {'code': 0} -> kakaoid가 없을 경우
    global serverdb
    cursor = serverdb.user.find({KAKAOID:kakaoid})
    res = list(cursor)
    if len(res) == 0: #정보가 없으면 0을 리턴
        return {'code':0}
    res = res[0]
    res['code'] = 1
    return res

def editUserInfo(kakaoid, dict):
    # dict = { NICKNAME : '바꿀 닉네임' } 으로 전달하면 해당 요소를 바꿈
    global serverdb
    if getUserInfoFromServer(kakaoid)['code'] == 0:
        print('editUserInfo : 해당 유저 찾을 수 없음',kakaoid)
        return {'code' : 0}
    idquery = { KAKAOID : kakaoid }
    values = { "$set" : dict }
    serverdb.user.update_one(idquery,values)
    editSession(kakaoid,dict)
    return {'code' : 1}

def delUserInfo(kakaoid):
    #회원탈퇴시 회원정보 삭제
    global serverdb
    if getUserInfoFromServer(kakaoid)['code'] == 0:
        print('delUserInfo : 해당 유저 찾을 수 없음',kakaoid)
        return {'code' : 0}
    idquery = { KAKAOID : kakaoid }
    serverdb.user.delete_one(idquery)
    return {'code' : 1}

if __name__ == "__main__":#Unit test를 위한 공간
    #serverDBinitiate()
    #createServerDummy()
    #editUserInfo('121815772',{NICKNAME:'asdfasdf'})
    #delUserInfo('12181577')
    #print(getUserInfoFromServer('12181577'))
    #print(getUserInfoFromServer('12181527'))

    sessionDBinitiate()
    serverDBinitiate()
    createSession('12181577')
    editSession('12181577',{NICKNAME : '더미더미'})
    print(getSessionInfo('12181577'))