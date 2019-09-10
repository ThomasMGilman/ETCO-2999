import CFG
import Bot
import time
import threading
import Globals

def main():
    cfg = CFG.chatConnection(Globals.HOST, Globals.PORT, Globals.OAUTH, Globals.USERNAME, Globals.CHANNEL, Globals.CLIENT_ID)
    lastMsg = time.time()
    Globals.tLock = threading.Lock()
    try:
        #create bot and attempt connection
        botSocket = Bot.bot(cfg)
        Globals.connected = botSocket.connect()

        while Globals.connected:
            tCount = Globals.getWorkerCount()
            if tCount < 1:
                t = threading.Thread(name="reciever",target=botSocket.recv)
                t.start()
            else:
                #Globals.printLockmsg(time.time() - lastMsg)
                if (time.time() - lastMsg) >= 1.0 and Globals.botQue.qsize() > 0:  # send a msg every 1second
                    botSocket.handleMsg()
                    lastMsg = time.time()
            time.sleep(1)
    finally:
        print("exiting")
        botSocket.sendMsg("Goodbye!!")
        botSocket.closeSocket()

main()