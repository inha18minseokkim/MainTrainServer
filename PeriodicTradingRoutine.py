from datetime import datetime, timedelta
import time
from loguru import logger

import AccountManager
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
        #logger.debug(tmpstr)
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
        logger.debug(f'{self.idx} 루틴 시작')
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
        todaylist: list[(str,int)] = self.schedulerqueue[self.idx]#얕은복사임
        targetlist: list[(str,int)] = self.schedulerqueue[(self.idx + 1) % 300]
        #todaylist의 요소들을 targetlist로 모두 옮겨
        while len(todaylist) == 0:
            curkakaoid , curlazyday = todaylist.pop(0)
            targetlist.append((curkakaoid,curlazyday+1))
        return {'code' : 1}
    def addNewAccount(self,kakaoid):
        trader: Trader.TradeManager = Trader.TradeManager()
        curaccount: AccountManager.Account = AccountManager.Account(kakaoid, self.serverdb)
        if isBusinessDay() == False: #오늘 영업일이 아닌경우 트레이드를 하지않고 내일로 미뤄
            logger.debug(f"{kakaoid} : 오늘 영업일이 아니라 거래를 못해 ㅎㅎ;;")
            nextidx: int = (self.idx + 1) % 300
            targetlist: list[(str, int)] = self.schedulerqueue[nextidx]
            targetlist.append((kakaoid, 0))
            return {'code' : 1}
    # 오늘 루틴이 끝났을 수 있기 때문에 오늘 추가되는건 따로 돌리고 큐에 넣는다
        rescode: int = trader.rebalance(curaccount)
        if rescode == 1:
            logger.debug(f'{kakaoid} 리밸런싱 완료')
        else:
            logger.debug(f'{kakaoid} 리밸런싱 중 문제가 생김')
    # 현재idx 큐가 아니라, 다음 큐(idx+period)에 추가해야된다
        nextidx : int = (self.idx + curaccount.period) % 300
        targetlist: list[(str,int)] = self.schedulerqueue[nextidx]
        targetlist.append((kakaoid,0))
        return {'code' : 1}
def background(scheduler : TradeScheduler):
    #main 루프 백그라운드에서 돌아갈 함수. 24시간마다 scheduler 큐의 각 인덱스 하나씩 순회하게 만드는 것이 목표.
    while True:
        curtime = datetime.now()
        if curtime.hour == 12 and curtime.minute == 0:
            scheduler.dailyRoutine() # 오늘 리밸런싱 해야되는 계정들 다 리밸런싱 돌려줌
            curtime = datetime.now() # 현재 시간
            nexttime = datetime(curtime.year,curtime.month,curtime.day,12,0,0,0) + timedelta(days=1) #내일 12시 시간
            dt = nexttime - curtime
            time.sleep(dt.seconds) #내일 12시 까지 남은 시간만큼 sleep

def isBusinessDay(): #오늘이 영업일인지 아닌지 판단해줌
    XKRX = ecals.get_calendar("XKRX")
    curdate = datetime.today().strftime("%Y-%m-%d")
    logger.debug(curdate)
    return XKRX.is_session(curdate)

if __name__ == "__main__":
    pass
    #maincontainer: Container.MainContainer = Container.MainContainer()
    #serdb: DBManager.ServerDBManager = maincontainer.serverdb_provider()
    # tmpscheduler: list[list[(str,int)]] = [[] for i in range(300)]
    # tmpscheduler[3].append(('12181577',3))
    # tmpscheduler[4].append(('2328479814',4))
    # tmpscheduler[3].append(('2350732802',2))
    # tmpscheduler[3].pop(0)
    #logger.debug(tmpscheduler)
    #serdb.setScheduler(tmpscheduler)
    #serdb.setSchedulerIdx(3)

    #scheduler: TradeScheduler = TradeScheduler(serdb)
    #scheduler.dailyRoutine()
    #logger.debug(scheduler.schedulerqueue)
    #logger.debug(scheduler.idx)
