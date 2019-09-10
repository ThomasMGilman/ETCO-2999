import socket
import Globals
import threading
import requests
import re

class bot:
    botSocket = None
    cfg = None
    def __init__(self, cfg):
        # create socket
        self.botSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cfg = cfg

    def closeSocket(self):
        self.botSocket.close()

    def sendMsg(self, msg):
        self.botSocket.send((msg+"\r\n").encode('utf-8'))

    def recv(self):
        Globals.printLockmsg("Worker Hired threadIdentity: {0}".format(threading.current_thread().getName()))
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
                Globals.printLockmsg("Got msg: {0} QueSize: {1}".format(response, Globals.botQue.qsize()))
            except Exception as e:
                None
                #Globals.printLockmsg("Got error: ".format(str(e)))

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

    def privateResponse(self, User, msg):
        self.sendMsg("PRIVMSG #{0} :{1}".format(User, msg))

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
            self.botSocket.settimeout(10.0)

            return True
        except Exception as e:
            print("failed to connect!!! {0}".format(e))
            return False

    def handleMsg(self):

        if not Globals.botQue.empty():
            response = Globals.getmsg()
            user = re.search(r"\w+", response).group()
            message = self.cfg.MSG_PATTERN.sub("", response).strip()

            Globals.printLockmsg("\n{0}: {1}".format(user, message))
            if (message.startswith("$Hello")):
                self.channelResponse("HI!!!")
            elif (message.startswith("$ColorTxt")):
                self.channelResponse("/me this is color text!!!")
            elif (message.startswith("$ByeFriend")):
                with Globals.tLock:
                    Globals.printLockmsg("YOUR ALL FIRED!!!")
                    Globals.Connected = False
                    Globals.EveryoneFired = False

                self.channelResponse("GoodBye Friends")
                self.channelResponse("/disconnect")
            elif (message.startswith("$cleanUp")):
                self.channelResponse("/clear")
                self.channelResponse("All clean!")
            elif(message.startswith("$recentClip")):
                try:
                    url = "https://api.twitch.tv/helix/clips?"+self.cfg.CHANNEL+"="
                    clipIndex = message[re.search(r"\d", message).start():]
                    Globals.printLockmsg("got: "+clipIndex)
                    req = requests.get(url, headers={'Client-ID' : self.cfg.CLIENT_ID})
                    data = req.json()
                    Globals.printLockmsg(data)
                except Exception as e:
                    Globals.printLockmsg(e)
            elif (message.startswith("$topGames")):
                try:
                    url = "https://api.twitch.tv/helix/games/top"
                    req = requests.get(url, headers={'Client-ID': self.cfg.CLIENT_ID})
                    data = req.json()['data']
                    Globals.printLockmsg(data)
                except Exception as e:
                    Globals.printLockmsg(e)
            elif (message.startswith("$Game")):
                try:
                    gameName = message[re.search(r"\s\w+", message).start()+1:]
                    url = "https://api.twitch.tv/helix/games?name="+gameName
                    req = requests.get(url, headers={'Client-ID': self.cfg.CLIENT_ID})
                    data = req.json()['data']
                    msg = ""
                    for i in range(len(data)):
                        msg += str(i) + ": \n\tID:" + data[i][0] + " Name: " + data[i][1] + "\n"  # appendName List
                    self.privateResponse(user, msg)
                    Globals.printLockmsg(data)
                except Exception as e:
                    Globals.printLockmsg(e)
        with Globals.tLock:
            Globals.threadCount -= 1
