from fastapi import APIRouter, Request, Response
import Declaration
import FinanceDataReader as fdr
from typing import Union
from pydantic import BaseModel
from enum import Enum

import Declaration
import Stock_Price

router = APIRouter()

@router.get("/getStockInfo/{code}")
async def getStockInfo(code: str):
    return Stock_Price.getStockInfo(code)

@router.get("/userinfo")
async def getUserInfo():
    return {"appkey": Declaration.appKey, "secret":Declaration.secret, "token": Declaration.token}

class Interval(Enum):
    YEAR = 'YEAR'
    MON = 'MON'
    WEEK = 'WEEK'
    DAY = 'DAY'
    HOUR = 'HOUR'
    MIN5 = 'MIN5'
    MIN1 = 'MIN1'

class Item(BaseModel):
    code: str
    interval: Interval
    start: str
    end: Union[str, None] = None

'''
005930 : 삼성전자
request body
{
    "interval": "YEAR",
    "code": "005930",
    "start": "2021"
}
'''
@router.post("/getPrice")
async def getChart(item: Item):
    df = fdr.DataReader(item.code, item.start)
    return df.to_dict()
