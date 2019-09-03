import CFG
import Bot
import time
import threading
import Globals

def main():
    cfg = CFG.chatConnection(Globals.HOST, Globals.PORT, Globals.OAUTH, Globals.USERNAME, Globals.CHANNEL)
    lastMsg = time.time()
    Globals.tLock = threading.Lock
    try:
        #create bot and attempt connection
        botSocket = Bot.bot(cfg)
        Globals.connected = botSocket.connect()

        while Globals.connected:
            try:
                tCount = Globals.getWorkerCount()
                if tCount < 1:
                    t = threading.Thread(target=botSocket.recv())
                    t.start()
                elif tCount < 2:
                    Globals.printLockmsg(time.time() - lastMsg)
                    if (time.time() - lastMsg) >= 1.0 and len(Globals.botQue) > 0:  # send a msg every 1second
                        botSocket.handleMsg()
                        lastMsg = time.time()

            except Exception as e:
                Globals.printLockmsg("Got error: {0}".format(str(e)))
            time.sleep(1)
    finally:
        print("exiting")
        botSocket.closeSocket()

main()