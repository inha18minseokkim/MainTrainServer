from fastapi import APIRouter
import DBManager

import AccountManager
import uuid
import Declaration
from loguru import logger
from dependency_injector import containers, providers
maincontainer = None
class MainContainer(containers.DeclarativeContainer):
    def __init__(self):
        logger.debug("DBContainer initiated")
    def __new__(cls):
        if not hasattr(cls, "_instance"):
            logger.debug("__new__ is called")
            cls._instance = super().__new__(cls)
        return cls._instance
    #dbmanager
    serverdb_provider = providers.Singleton(DBManager.ServerDBManager)
    sessiondb_provider = providers.Singleton(DBManager.SessionDBManager)
    #trader 도메인 기능
#    trade_provider = providers.Factory(Trader.TradeManager,_sessiondb=sessiondb_provider,_serverdb=serverdb_provider)
router = APIRouter()
@router.get('/test?param={par}')
async def fortest(par: str):
    return par

#유저 정보 관련 API
@router.get('/getUserInfo/{uuid}')
async def getUserInfo(uuid: str):
    global maincontainer
    maincontainer = MainContainer()
    logger.debug(maincontainer)
    logger.debug(uuid)
    sesdb: DBManager.SessionDBManager = maincontainer.sessiondb_provider()
    res = sesdb.getSessionInfo(uuid)
    logger.debug(res,type(res))
    del res['_id']
    return res
@router.get('/setUserNickName/{uuid}/{target}')
async def setUserNickName(uuid: str, target: str):
    global maincontainer
    maincontainer = MainContainer()
    sesdb: DBManager.SessionDBManager = maincontainer.sessiondb_provider()
    serdb = DBManager.ServerDBManager = maincontainer.serverdb_provider()
    rescode = sesdb.editSession(uuid,{DBManager.NICKNAME:target},serdb)['code']
    return {'code' : rescode}
@router.get('/setUserRatio/{uuid}/{tostr}')
async def setUserRatio(uuid: str, tostr: str):
    global maincontainer
    maincontainer = MainContainer()
    sesdb: DBManager.SessionDBManager = maincontainer.sessiondb_provider()
    serdb: DBManager.ServerDBManager = maincontainer.serverdb_provider()
    try:
        targetdict = dict(eval(tostr))
    except:
        return {'code' : 0, 'msg' : 'tostr 문자열이 올바르지 않습니다'}
    rescode = sesdb.editSession(uuid,{DBManager.STKLST : tostr})
    return {'code' : rescode}


if __name__ == "__main__":#Unit test를 위한 공간
    Declaration.initiate()
    #이런식으로 인스턴스 생성하시면 싱글톤 패턴으로 구현됩니다
    serverdb = MainContainer().serverdb_provider()
    sessiondb = MainContainer().sessiondb_provider()
    #sessiondb2 = MainContainer().sessiondb_provider()
    tmpuuid = sessiondb.createSession('12181577','tokensample',serverdb)[DBManager.UUID]
    logger.debug(tmpuuid,uuid.UUID(tmpuuid))
    logger.debug(sessiondb.createSession('121815777','adsfasdfdas',serverdb))
    logger.debug(sessiondb.editSession(tmpuuid,{DBManager.NICKNAME:'김민석석'},serverdb))
    #logger.debug(sessiondb2.getSessionInfo(tmpuuid))
    logger.debug(sessiondb.editSession(tmpuuid,{DBManager.NICKNAME:'민석김김'},serverdb))
    logger.debug(sessiondb.getSessionInfo(tmpuuid))
    trader = MainContainer().trade_provider()
    #logger.debug(trader.buyMarketPrice(tmpuuid,'005930',1))
    account = AccountManager.Account(tmpuuid,sessiondb,serverdb)
    logger.debug(account.ratio)
    sessiondb2 = MainContainer().sessiondb_provider()
    logger.debug(sessiondb2.getSessionInfo(tmpuuid))