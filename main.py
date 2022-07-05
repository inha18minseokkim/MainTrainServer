from fastapi import FastAPI
import json,requests
from fastapi import FastAPI
import Stock_Price
import Declaration
app = FastAPI()

@app.on_event("startup") #시작 시 실행되는 메소드 나중에 로그인으로 구현해야 함.
async def on_app_start() -> None:
    Declaration.initiate()

@app.get("/getStockInfo/{code}")
async def getStockInfo(code):
    return Stock_Price.getStockInfo(code)
@app.get("/userinfo")
async def getUserInfo():
    return {"appkey": Declaration.appKey, "secret":Declaration.secret, "token": Declaration.token}

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
