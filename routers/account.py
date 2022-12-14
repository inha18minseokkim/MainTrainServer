
from loguru import logger
import uuid

from fastapi import APIRouter, Request, Query, Depends
from pydantic import BaseModel


import DBManager
import AccountManager
import Declaration
from dependencies import get_uuid, get_sesdb, get_serdb, get_scheduler

router = APIRouter()
@router.get('/asdf')
async def asdf():
    return "ASDFASDFASFASDF"
@router.get('/test?param={par}')
async def fortest(par: str):
    return par


class U(BaseModel):
    target: str


class UI(BaseModel):
    target: int

@router.get('/getUserInfo2')
async def getUserInfo2(uuid: str, sesdb = Depends(get_sesdb), serdb = Depends(get_serdb)):
    res = sesdb.getSessionInfo(uuid)
    if res['code'] == 0:
        logger.debug(f'{uuid} : 세션이 유효하지 않거나 세션 정보와 맞는 계정이 없습니다')
        return {'code': 0, 'msg': f'{uuid} : 세션이 유효하지 않거나 세션 정보와 맞는 계정이 없습니다'}
    tmpkakaoid = res[DBManager.KAKAOID]
    tmpaccount: AccountManager = AccountManager.Account(tmpkakaoid, serdb)
    tmpres: dict = tmpaccount.getAccountInfoDictionary()
    tmpres['code'] = 1
    return tmpres
#유저 정보 관련 API
@router.post('/getUserInfo', tags=['사용자정보 관련'])
async def getUserInfo(item: U, uuid = Depends(get_uuid), sesdb = Depends(get_sesdb)):
    res = sesdb.getSessionInfo(uuid)
    logger.debug(res,type(res))
    del res['_id']
    return res


@router.post(path = '/getUserAccount', name = '사용자 잔고정보 반환', tags=['사용자정보 관련'], description = 'uuid에 해당하는 고객의 잔고정보 리턴',
            response_description='code - 1 : 유효한 response, 0 : 뭔가 문제가 있는 response<br>'
                                 'state - 1 : 유효한 계정 정보, 0 : 서버에서 조회 실패<br>'
                                 'kakaoid : 현재 유저의 kakaoid<br>'
                                 'nickname : 현재 유저가 사용하고 있는 닉네임<br>'
                                 'apikey : 유저가 입력한 한국투자 api key <br>'
                                 'secret : 유저가 입력한 한국투자 secret<br>'
                                 'quantity : 유저가 포트폴리오 운용을 위해 설정한 한도 금액 <br>'
                                 'cano : 유저의 한국투자 계좌 앞 8자리 <br>'
                                 'acnt : 유저의 한국투자 계좌 뒤 2자리 <br>'
                                 'ratio : 유저가 처음에 포트폴리오 설정해놓은 금액<br>'
                                 'total : 유저 잔고 총평가금액(예수금+유가평가금액 총합)<br>'
                                 'deposit : 예수금총액<br>'
                                 'eval : 유가평가금액, 매수한 주식의 총 평가액<br>'
                                 'sumofprch : 주식을 매입한 당시 가격의 총합 <br>'
                                 'sumofern : 평가손익합계금액<br>'
                                 'assticdc : 자산증감액<br>'
                                 'assticdrct : 자산증감수익률<br>'
                                 'curaccount : 현재 가지고 있는 자산들의 정보<br>'
                                 'favlist : 현재 유저가 저장해놓은 즐겨찾기 리스트, 콤마로 구분한다. ex) "삼성전자,LG,삼성전자우,KODEX 은행" ')


async def getUserAccount(request: Request, uuid = Depends(get_uuid), sesdb = Depends(get_sesdb), serdb = Depends(get_serdb)):
    res = sesdb.getSessionInfo(uuid)
    logger.debug(f"{res} {uuid}")
    if res['code'] == 0:
        logger.debug(f'{uuid} : 세션이 유효하지 않거나 세션 정보와 맞는 계정이 없습니다')
        return {'code' : 0, 'msg' : f'{uuid} : 세션이 유효하지 않거나 세션 정보와 맞는 계정이 없습니다'}
    tmpkakaoid = res[DBManager.KAKAOID]
    tmpaccount: AccountManager = AccountManager.Account(tmpkakaoid,serdb)
    tmpres:dict = tmpaccount.getAccountInfoDictionary()
    tmpres['code'] = 1
    return tmpres


@router.post('/setUserNickName', name = '사용자 닉네임 수정',tags=['사용자정보 관련'], description = 'uuid에 해당하는 사용자 닉네임 수정')
async def setUserNickName(item: U, uuid = Depends(get_uuid), sesdb = Depends(get_sesdb), serdb = Depends(get_serdb)):
    target = item.target
    rescode = sesdb.editSession(uuid,{DBManager.NICKNAME:target},serdb)['code']
    resp = {'code' : rescode}
    if rescode == 0: resp['msg'] = f'{uuid} {target} 수정 실패'
    return resp


@router.post('/setUserApiKey', name = '사용자 apikey 수정', tags=['사용자정보 관련'])
async def setUserApiKey(item: U, uuid = Depends(get_uuid), sesdb = Depends(get_sesdb), serdb = Depends(get_serdb)):
    target = item.target
    rescode = sesdb.editSession(uuid, {DBManager.APIKEY: target}, serdb)['code']
    resp = {'code': rescode}
    if rescode == 0: resp['msg'] = f'{uuid} {target} 수정 실패'
    return resp


@router.post('/setUserSecret', name = '사용자 secret 수정',tags=['사용자정보 관련'])
async def setUserSecret(item: U, uuid = Depends(get_uuid), sesdb = Depends(get_sesdb), serdb = Depends(get_serdb)):
    target = item.target
    rescode = sesdb.editSession(uuid, {DBManager.SECRET: target}, serdb)['code']
    resp = {'code': rescode}
    if rescode == 0: resp['msg'] = f'{uuid} {target} 수정 실패'
    return resp


@router.post('/setUserQuantity',name = '사용자 운용금액 한도 수정', tags=['사용자정보 관련'])
async def setUserQuantity(item: UI, uuid = Depends(get_uuid), sesdb = Depends(get_sesdb), serdb = Depends(get_serdb)):
    target = item.target
    rescode = sesdb.editSession(uuid, {DBManager.QUANTITY: target}, serdb)['code']
    resp = {'code': rescode}
    if rescode == 0: resp['msg'] = f'{uuid} {target} 수정 실패'
    return resp


@router.post('/setUserCANO',name = '사용자 CANO 수정', tags=['사용자정보 관련'])
async def setUserCANO(item: U, uuid = Depends(get_uuid), sesdb = Depends(get_sesdb), serdb = Depends(get_serdb)):
    target = item.target
    rescode = sesdb.editSession(uuid, {DBManager.CANO: target}, serdb)['code']
    resp = {'code': rescode}
    if rescode == 0: resp['msg'] = f'{uuid} {target} 수정 실패'
    return resp


@router.post('/setUserACNT',name = '사용자 ACNT 수정', tags=['사용자정보 관련'])
async def setUserACNT(item: U, uuid = Depends(get_uuid), sesdb = Depends(get_sesdb), serdb = Depends(get_serdb)):
    target = item.target
    rescode = sesdb.editSession(uuid, {DBManager.ACNT: target}, serdb)['code']
    resp = {'code': rescode}
    if rescode == 0: resp['msg'] = f'{uuid} {target} 수정 실패'
    return resp


@router.post('/setUserRatio',name = '사용자 설정 비율 수정', tags=['사용자정보 관련'],
            description='유의하셔야 할 점 : 반드시 코드:비율 형태를 지켜주세요. tostr은 딕셔너리,json자료형을 문자열형태로 받습니다. 모든 비율의 합은 1이어야 합니다.<br>'
                        'ex) { "005930" : "0.5", "003550" : "0.3", "091170" : "0.2" }')
async def setUserRatio(item: U, uuid = Depends(get_uuid), sesdb = Depends(get_sesdb), serdb = Depends(get_serdb)):
    tostr = item.target
    try:
        targetdict = dict(eval(tostr))
    except:
        return {'code' : 0, 'msg' : 'tostr 문자열이 올바르지 않습니다'}
    rescode = sesdb.editSession(uuid,{DBManager.STKLST : tostr} ,serdb)['code']
    resp = {'code': rescode}
    if rescode == 0: resp['msg'] = f'{uuid} {tostr} 수정 실패'
    return resp


@router.post('/setUserFavList', name ='사용자 즐거찾기 리스트 수정', tags=['사용자정보 관련'],
            description='원본 데이터를 모두 지우는 작업이기 때문에 api를 호출 할 때 반드시 리스트를 넘겨주세요'
                        ' ex) 삼성전자,LG,삼성전자우,KODEX%20은행 에서 삼성전자를 없애고싶으면 LG,삼성전자우,KODEX%20은행'
                        '를 넘겨주셔야 합니다')
async def setUserFavList(item: U, uuid = Depends(get_uuid), sesdb = Depends(get_sesdb), serdb = Depends(get_serdb)):
    tostr = item.target
    try:
        targetdict = tostr.split(',')
    except:
        return {'code': 0, 'msg': 'tostr 문자열이 올바르지 않습니다'}
    rescode = sesdb.editSession(uuid, {DBManager.FAVLST: tostr}, serdb)['code']
    resp = {'code': rescode}
    if rescode == 0: resp['msg'] = f'{uuid} {tostr} 수정 실패'
    return resp
#유저 정보 관련 API


@router.post('/getModelInfo', tags=['모델 정보 관련'])
async def getUserInfo(serdb = Depends(get_serdb)):
    res = serdb.getModelInfo()
    logger.debug(f'{res},{type(res)}')
    for i in res:
        del i['_id']
    return res





if __name__ == "__main__":#Unit test를 위한 공간
    Declaration.initiate()
    #이런식으로 인스턴스 생성하시면 싱글톤 패턴으로 구현됩니다
    serverdb = get_serdb()
    sessiondb = get_sesdb()
    #sessiondb2 = MainContainer().sessiondb_provider()
    tmpuuid = sessiondb.createSession('12181577','tokensample',serverdb)[DBManager.UUID]
    logger.debug(tmpuuid,uuid.UUID(tmpuuid))
    logger.debug(sessiondb.createSession('121815777','adsfasdfdas',serverdb))
    logger.debug(sessiondb.editSession(tmpuuid,{DBManager.NICKNAME:'김민석석'},serverdb))
    #logger.debug(sessiondb2.getSessionInfo(tmpuuid))
    logger.debug(sessiondb.editSession(tmpuuid,{DBManager.NICKNAME:'민석김김'},serverdb))
    logger.debug(sessiondb.getSessionInfo(tmpuuid))
    # trader = MainContainer().trade_provider()
    #logger.debug(trader.buyMarketPrice(tmpuuid,'005930',1))
    account = AccountManager.Account(tmpuuid,sessiondb,serverdb)
    logger.debug(account.ratio)
    sessiondb2 = get_sesdb()
    logger.debug(sessiondb2.getSessionInfo(tmpuuid))