import threading

from fastapi import FastAPI
import contextvars
from loguru import logger
import DBManager
import PeriodicTradingRoutine
import Declaration
from routers import investment, test, login, account
from starlette.middleware.cors import CORSMiddleware
from dependencies import get_uuid, get_sesdb, get_serdb, get_scheduler

app = FastAPI()
app.include_router(investment.router, prefix='')
app.include_router(test.router, prefix='')
app.include_router(login.router, prefix='')
app.include_router(account.router,prefix='')

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

request_id_contextvar = contextvars.ContextVar("request_id", default=None)

@app.on_event("startup") #시작 시 실행되는 메소드 나중에 로그인으로 구현해야 함.
async def on_app_start() -> None:
    Declaration.initiate()
    sesdb = await get_sesdb()
    serdb = await get_serdb()
    scheduler = await get_scheduler()
    #trader = maincontainer.trade_provider()
    tmpuuid = sesdb.createSession('12181577', 'token', serdb)[DBManager.UUID] #테스트용 더미세션.
    logger.debug(tmpuuid)
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

    sesdb = maincontainer.sessiondb_provider()
    # logger.debug(f"[{request_id}] Request Started")

    if 'uuid' in request.headers.keys():
        uid = request.headers.get('uuid')
        if sesdb.validateToken(uid)['code'] == 0:
            return JSONResponse(content={"Error": "UUID is not found"}, status_code=401)
    
    return await call_next(request)
    
    
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
