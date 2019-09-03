import queue
import threading

HOST = "irc.chat.twitch.tv"
PORT = 6667
OAUTH = "w74fi7jcegv41r2b2x25ktidpyb7vq"
USERNAME = "bFriend"
CHANNEL = "nilkin1"

threadCount = 0
botQue = queue.Queue()
lastMsg = 0.0

connected = False
EveryoneFired = False

tLock = threading.RLock()

def printLockmsg(msg):
    with tLock:
        print(msg)

def getWorkerCount():
    return threadCount