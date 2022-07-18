import DBManager
import Trader
import AccountManager
import uuid
import Declaration
from dependency_injector import containers, providers
class MainContainer(containers.DeclarativeContainer):
    def __init__(self):
        print("DBContainer initiated")
    def __new__(cls):
        if not hasattr(cls, "_instance"):
            print("__new__ is called")
            cls._instance = super().__new__(cls)
        return cls._instance
    #dbmanager
    serverdb_provider = providers.Singleton(DBManager.ServerDBManager)
    sessiondb_provider = providers.Singleton(DBManager.SessionDBManager)
    #trader 도메인 기능
    trade_provider = providers.Factory(Trader.TradeManager,_sessiondb=sessiondb_provider,_serverdb=serverdb_provider)

if __name__ == "__main__":#Unit test를 위한 공간
    Declaration.initiate()
    #이런식으로 인스턴스 생성하시면 싱글톤 패턴으로 구현됩니다
    serverdb = MainContainer().serverdb_provider()
    sessiondb = MainContainer().sessiondb_provider()
    #sessiondb2 = MainContainer().sessiondb_provider()
    tmpuuid = sessiondb.createSession('12181577','tokensample',serverdb)[DBManager.UUID]
    print(tmpuuid,uuid.UUID(tmpuuid))
    print(sessiondb.createSession('121815777','adsfasdfdas',serverdb))
    print(sessiondb.editSession(tmpuuid,{DBManager.NICKNAME:'김민석석'},serverdb))
    #print(sessiondb2.getSessionInfo(tmpuuid))
    print(sessiondb.editSession(tmpuuid,{DBManager.NICKNAME:'민석김김'},serverdb))
    print(sessiondb.getSessionInfo(tmpuuid))
    trader = MainContainer().trade_provider()
    #print(trader.buyMarketPrice(tmpuuid,'005930',1))
    account = AccountManager.Account(tmpuuid,sessiondb,serverdb)
    print(account.ratio)
    sessiondb2 = MainContainer().sessiondb_provider()
    print(sessiondb2.getSessionInfo(tmpuuid))