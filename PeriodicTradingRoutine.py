from loguru import logger

import AccountManager
import Container
import DBManager


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
        self.schedulerqueue = tmpstr
    def savetoServerDB(self):#서버가 꺼지는것을 대비해 db에 주기적으로 저장
        saver: list[list[(str,int)]] = [[] for i in range(300)]
        for i in range(300):
            for ac,cnt in self.schedulerqueue[i]:
                saver[i].append((ac, cnt)) #AccountManager에 있는 kakaoid만 빼서 저장
        serdb.setScheduler(saver)

    def dailyRoutine(self):#매일 해당 idx의 큐에 대해
        pass
    def moveToNext(self):#해당 날짜가 영업일이 아닌 경우 다음 큐로 옮긴다.
        pass

if __name__ == "__main__":
    maincontainer: Container.MainContainer = Container.MainContainer()
    serdb: DBManager.ServerDBManager = maincontainer.serverdb_provider()
    tmpscheduler: list[list[(str,int)]] = [[] for i in range(300)]
    tmpscheduler[3].append(('12181577',3))
    tmpscheduler[4].append(('2328479814',4))
    tmpscheduler[3].append(('2350732802',2))
    #logger.debug(tmpscheduler)
    serdb.setScheduler(tmpscheduler)
    scheduler: TradeScheduler = TradeScheduler(serdb)
