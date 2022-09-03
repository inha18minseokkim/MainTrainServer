from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer

from loguru import logger

import DBManager
import PeriodicTradingRoutine
from dependency_injector import containers, providers

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
    scheduler_provider = providers.Singleton(PeriodicTradingRoutine.TradeScheduler, _serverdb = serverdb_provider)
    #trader 도메인 기능
#    trade_provider = providers.Factory(Trader.TradeManager,_sessiondb=sessiondb_provider,_serverdb=serverdb_provider)
container = MainContainer()


async def get_sesdb():
    return container.sessiondb_provider()


async def get_serdb():
    return container.serverdb_provider()


async def get_scheduler():
    return container.scheduler_provider()


oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="token", authorizationUrl="authorization")


async def get_uuid(sesdb = Depends(get_sesdb), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if sesdb.validateToken(token)['code'] == 0:
        return credentials_exception
    return token