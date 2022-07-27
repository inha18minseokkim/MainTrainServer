from datetime import datetime

from loguru import logger

import AccountManager
import Container
import DBManager
import Trader
import exchange_calendars as ecals

class TradeScheduler:
    def __init__(self, _serverdb : DBManager.ServerDBManager):
        self.schedulerqueue: list[list[(str,int)]] = [[] for i in range(300)]
        #Account 객체는 트레이딩 할 객체, int는 밀린 날짜 수
        self.idx: int = 0
        self.serverdb: DBManager.ServerDBManager = _serverdb
        self.loadfromServerDB()
    def loadfromServerDB(self): #서버가 꺼졌다가 켜지면 db에서 그 전까지 내용 다 받아옴
        tmpstr = self.serverdb.getScheduler()
        logger.debug(tmpstr)
        for i in range(300):
#            logger.debug(tmpstr['value'])
            self.schedulerqueue[i] = list(tmpstr[i]['value'])
        self.idx = self.serverdb.getSchedulerIdx()
    def savetoServerDB(self):#서버가 꺼지는것을 대비해 db에 주기적으로 저장
        saver: list[list[(str,int)]] = [[] for i in range(300)]
        for i in range(300):
            for ac,cnt in self.schedulerqueue[i]:
                saver[i].append((ac, cnt)) #AccountManager에 있는 kakaoid만 빼서 저장
        self.serverdb.setScheduler(saver)
        self.serverdb.setSchedulerIdx(self.idx)
    def dailyRoutine(self):#매일 해당 idx의 큐에 대해
        if isBusinessDay() == False: #오늘이 영업일이 아니라면
            self.moveToNext() #오늘 셀안에 있는 element를 내일 셀로 옮김
            return {'code' : 1}
        #오늘이 영업일이라면 리밸런싱 수행
        todaylist: list[(str,int)] = self.schedulerqueue[self.idx]
        logger.debug(todaylist)
        while len(todaylist) != 0:
            curkakaoid, curlazyday = todaylist.pop(0) #현재 카카오아이디와 lazyday 추출
            curaccount: AccountManager.Account = AccountManager.Account(curkakaoid, self.serverdb) #리밸런싱을 위해 객체 생성
            trader: Trader.TradeManager = Trader.TradeManager()
            # 현재 idx에 있는 친구들의 리밸런싱을 수행한다
            rescode: int = trader.rebalance(curaccount)['code']
            if rescode == 1:
                logger.debug(f'{curaccount.kakaoid} 리밸런싱 완료')
            else:
                logger.debug(f'{curaccount.kakaoid} 리밸런싱 중 문제가 생김')
            # 현재 idx에 있는 친구들을 다음 인덱스에 넣는다
            nextidx: int = (self.idx + curaccount.period - curlazyday) % 300 #다음 리밸런싱 날짜 = 현재 idx + 사용자지정 간격 - 밀린만큼 % 300
            if curaccount.period < curlazyday: #curlazyday가 너무 커서(추석같은 경우 계속밀림) 이전 인덱스로 넘어가는 경우
                nextidx = (self.idx + curaccount.period) % 300 # 그냥 curlazyday를 무시해
            targetlist: list[(str, int)] = self.schedulerqueue[nextidx]
            targetlist.append((curkakaoid,0))
        self.idx = (self.idx + 1) % 300 #오늘 할일 끝났으니 내일 인덱스로 옮겨
        self.savetoServerDB()
        return {'code' : 1}
    def moveToNext(self):#해당 날짜가 영업일이 아닌 경우 다음 큐로 옮긴다.
        todaylist: list[(str,int)] = self.schedulerqueue[self.idx]
        targetlist: list[(str,int)] = self.schedulerqueue[(self.idx + 1) % 300]
        #todaylist의 요소들을 targetlist로 모두 옮겨
        while len(todaylist) == 0:
            curkakaoid , curlazyday = todaylist.pop(0)
            targetlist.append((curkakaoid,curlazyday+1))
        return {'code' : 1}

def isBusinessDay(): #오늘이 영업일인지 아닌지 판단해줌
    XKRX = ecals.get_calendar("XKRX")
    curdate = datetime.today().strftime("%Y-%m-%d")
    logger.debug(curdate)
    return XKRX.is_session(curdate)

if __name__ == "__main__":
    maincontainer: Container.MainContainer = Container.MainContainer()
    serdb: DBManager.ServerDBManager = maincontainer.serverdb_provider()
    # tmpscheduler: list[list[(str,int)]] = [[] for i in range(300)]
    # tmpscheduler[3].append(('12181577',3))
    # tmpscheduler[4].append(('2328479814',4))
    # tmpscheduler[3].append(('2350732802',2))
    # tmpscheduler[3].pop(0)
    #logger.debug(tmpscheduler)
    #serdb.setScheduler(tmpscheduler)
    #serdb.setSchedulerIdx(3)

    scheduler: TradeScheduler = TradeScheduler(serdb)
    scheduler.dailyRoutine()
    logger.debug(scheduler.schedulerqueue)
    logger.debug(scheduler.idx)