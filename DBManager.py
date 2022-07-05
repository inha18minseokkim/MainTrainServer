import pymongo as pymongo
import pymongo_inmemory
import Declaration
sessiondb = None
serverdb = None
#sessiondb : 세션을 유지하기 위해 사용하는 inmemory DB
#serverdb : 서버에 저장되어 있는 데이터들을 불러오는 db, mongodb atlas를 사용함
#inmemorydb는 껐다 키면 사라지니 세션 유지용으로만 사용!!
def sessionDBinitiate(): #로컬 저장소에 있는 inmemory DB
    global sessiondb
    client = pymongo_inmemory.MongoClient()
    sessiondb = client.sessionDB


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
    client = pymongo.MongoClient(
        f"mongodb+srv://admin:{Declaration.modelDBPW}@cluster0.qbpab.mongodb.net/?retryWrites=true&w=majority")
    serverdb = client.TradingDB