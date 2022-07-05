import pymongo as pymongo
import pymongo_inmemory
import Declaration
sessiondb = None
serverdb = None
#sessiondb : 세션을 유지하기 위해 사용하는 inmemory DB
#serverdb : 서버에 저장되어 있는 데이터들을 불러오는 db, mongodb atlas를 사용함
#inmemorydb는 껐다 키면 사라지니 세션 유지용으로만 사용!!
#dictionary key는 아래 값들을 명시적으로 사용 권장(오타 방지를 위해)
KAKAOID = 'kakaoid'
NICKNAME = 'nickname'
APIKEY = 'apikey'
SECRET = 'secret'
QUANTITY = 'quantity'
MODEL = 'model'
def sessionDBinitiate(): #로컬 저장소에 있는 inmemory DB
    global sessiondb
    #세션을 저장하는 용도로만 사용
    # kakaoid : "카카오 아이디 String"
    # nickname : "사용자 닉네임 String"
    # apikey : "한국투자 apikey String"
    # secret : "한국투자 api secret String"
    # quantity : "현재 투자 설정 한 금액 Int"
    # **저장되어있는 카카오아이디 -> 현재 세션 유지중, 저장안되어있음 -> 세션 없는것
    client = pymongo_inmemory.MongoClient()
    sessiondb = client.sessionDB
    print("sessiondb 초기화 완료",sessiondb)

def createDummyData(): #Unit test용 페이크 데이터 하나 만들어서 세션db에 넣음
    global sessiondb
    sessiondb.user.insert_one({KAKAOID:'12181577',NICKNAME:'김민석',APIKEY:'asdf',SECRET:'sec',QUANTITY: 1000000})

def isSessionAvailable(kakaoid): #api를 호출 하기 전 해당 세션이 있는지
    global sessiondb
    cursor = sessiondb.user.find({KAKAOID: kakaoid})
    res = list(cursor)
    #카카오아이디를 파라미터로 받아서 현재 세션db에 존재하면 1, 존재하지않으면 0 리턴
    if res: return 1
    else: return 0



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

def createServerDummy():
    global serverdb
    serverdb.user.insert_one({KAKAOID: '12181577', NICKNAME: '김민석', APIKEY: 'asdf', SECRET: 'sec', QUANTITY: 1000000})
def getUserInfoFromServer(kakaoid):
    global serverdb
    cursor = serverdb.user.find({KAKAOID:kakaoid})
    res = list(cursor)
    print(res[0])
    return res[0]
def isRegistered(kakaoid):
    return
def editUserInfo(kakaoid, dict):
    return
if __name__ == "__main__":#Unit test를 위한 공간
    serverDBinitiate()
    createServerDummy()
    getUserInfoFromServer('12181577')
    #sessionDBinitiate()
    #createDummyData()
    #print(isSessionAvailable('12181577'))