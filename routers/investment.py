from fastapi import APIRouter

router = APIRouter()

@router.get("/getStockInfo/{code}")
async def getStockInfo(code):
    return Stock_Price.getStockInfo(code)

@router.get("/userinfo")
async def getUserInfo():
    return {"appkey": Declaration.appKey, "secret":Declaration.secret, "token": Declaration.token}