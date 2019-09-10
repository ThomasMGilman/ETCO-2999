import queue
import threading

HOST = "irc.chat.twitch.tv"
PORT = 6667
OAUTH = "w74fi7jcegv41r2b2x25ktidpyb7vq"
USERNAME = "bFriend"
CHANNEL = "nilkin1"
CLIENT_ID = 'e5ynnitdgyrp79prsv47rm9cuhxwvu'

threadCount = 0
botQue = queue.Queue()
lastMsg = 0.0

connected = False
EveryoneFired = False

tLock = threading.Lock()

def printLockmsg(msg):
    tLock.acquire()
    print(msg)
    tLock.release()


def getWorkerCount():
    return threadCount

def getmsg():
    if botQue is None or botQue.qsize() <=0:
        return None
    else:
        return botQue.get()