import socket
import Globals
import queue
import re

class bot:
    botSocket = None
    cfg = None
    def __init__(self, cfg):
        # create socket
        self.botSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.botSocket.settimeout(1)
        self.cfg = cfg

    def closeSocket(self):
        self.botSocket.close()

    def sendMsg(self, msg):
        self.botSocket.send((msg+"\r\n").encode('utf-8'))

    def recv(self):
        Globals.printLockmsg("Worker Hired")
        with Globals.tLock:
            Globals.threadCount += 1

        threadAtWork = True
        while threadAtWork:
            try:
                response = self.botSocket.recv(2048).decode("utf-8")
                if response.startswith("PING"):  # respond to server to keep alive
                    self.keepAlive()
                else:
                    Globals.botQue.put(response)
            except Exception as e:
                Globals.printLockmsg("Got error: ".format(str(e)))

            Globals.tLock.acquire()
            if Globals.EveryoneFired:
                threadAtWork = False
            Globals.tLock.release()

        with Globals.tLock:
            Globals.threadCount -= 1

        Globals.printLockmsg("Fired worker, no benefits given")

    def queMsg(self, msg):
        Globals.botQue.append(msg)

    def announceArrival(self):
        self.sendMsg("PRIVMSG #{0} :{1} has arrived!!!".format(self.cfg.CHANNEL, self.cfg.BOT_USERNAME))
        self.sendMsg("/mod {0}".format(self.cfg.CHANNEL))

    def channelResponse(self, msg):
        self.sendMsg("PRIVMSG #{0} :{1}".format(self.cfg.CHANNEL, msg))

    def keepAlive(self):
        self.sendMsg("PONG :tmi.twitch.tv")

    def connect(self):
        # attempt connection
        try:
            self.botSocket.connect((self.cfg.HOST, self.cfg.PORT));
            self.sendMsg("PASS oauth:{0}".format(self.cfg.OAUTH))
            self.sendMsg("NICK {0}".format(self.cfg.BOT_USERNAME))
            self.sendMsg("JOIN #{0}".format(self.cfg.CHANNEL))
            self.announceArrival()

            return True
        except Exception as e:
            print("failed to connect!!! {0}".format(e))
            return False

    def handleMsg(self):
        Globals.printLockmsg("Messanger hired")
        with Globals.tLock:
            Globals.threadCount += 1

        if not Globals.botQue.empty():
            response = Globals.botQue.pop(0)
            user = re.search(r"\w+", response).group()
            message = self.cfg.MSG_PATTERN.sub("", response).strip()

            Globals.printLockmsg("{0}: {1}".format(user, message))
            if (message.startswith("$Hello")):
                self.channelResponse("HI!!!")
            elif (message.startswith("$ColorTxt")):
                self.channelResponse("/me this is color text!!!")
            elif (message.startswith("$ByeFriend")):
                Globals.tLock.acquire()
                Globals.printLockmsg("YOUR ALL FIRED!!!")
                Globals.EveryoneFired = False
                Globals.Connected = False
                Globals.tLock.release()
                self.channelResponse("GoodBye Friends")
                self.channelResponse("/disconnect")
            elif (message.startswith("$cleanUp")):
                self.channelResponse("/clean")
                self.channelResponse("All clean!")
        with Globals.tLock:
            Globals.threadCount -= 1

        Globals.printLockmsg("Messanger put out of their missery violently with a shot to the head")
