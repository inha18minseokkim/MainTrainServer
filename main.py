import asyncio
import threading

from fastapi import FastAPI, Request, BackgroundTasks
import json,requests,random,uuid,contextvars,time
from fastapi.responses import JSONResponse
from loguru import logger
import DBManager
import PeriodicTradingRoutine
import Stock_Price
import AccountManager
import Declaration
from routers import investment,test,login
from pydantic import BaseModel
import Container
from Container import maincontainer
from starlette.middleware.cors import CORSMiddleware
# session 인증 안받는 api 목록
whiteList = ['/login', '/auth', ] 

app = FastAPI()
app.include_router(investment.router, prefix='')
app.include_router(test.router, prefix='')
app.include_router(login.router, prefix='')
app.include_router(Container.router,prefix='')

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
)

request_id_contextvar = contextvars.ContextVar("request_id", default=None)

@app.on_event("startup") #시작 시 실행되는 메소드 나중에 로그인으로 구현해야 함.
async def on_app_start() -> None:
    global maincontainer
    Declaration.initiate()
    maincontainer = Container.MainContainer()
    sesdb = maincontainer.sessiondb_provider()
    serdb = maincontainer.serverdb_provider()
    #trader = maincontainer.trade_provider()
    tmpuuid = sesdb.createSession('12181577','token',serdb)[DBManager.UUID] #테스트용 더미세션.
    logger.debug(tmpuuid)
    scheduler: PeriodicTradingRoutine.TradeScheduler = maincontainer.scheduler_provider()
    threading.Thread(target = PeriodicTradingRoutine.background, args = (scheduler,)).start()

'''
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    request_id_contextvar.set(request_id)
    
    ip = request['client'][0]
    port = request['client'][1]
    client = f"{ip}:{port}"

    logger.debug(f"[{request_id}] Request Started")


    # 모든 api에 세션 인증 일괄 적용
    
    if reuqest['path'] not in whilteList:
        body = await request.json()
        seesionId = body.get('access')
        if DBManager.getSessionInfo(seesionId) == 0:
            return JSONResponse(content={"error": "Unauthorized"}, status_code=401)
    

    try:
        return await call_next(request)

    except Exception as e:
        logger.debug(f"[{request_id}] Request Failed: {e}")
        return JSONResponse(content={"Success": False}, status_code=500)

    finally:
        assert request_id_contextvar.get() == request_id
        process_time = time.time() - start_time
        logger.debug(f"[{request_id}] Request Ended {process_time} Seconds")
'''