import socket
import Globals
import threading
import requests
import os.path;
import re

class bot:
    botSocket = None
    cfg = None

    def __init__(self, cfg):
        # create socket
        self.botSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cfg = cfg
        botfile = open(os.path.join(os.getcwd(), "Bot.py"), "r+")

        for line in botfile:
            #Globals.printLockmsg(line)
            regex = r"\$.*\""
            match = re.findall(regex, line) #Globals.printLockmsg()
            for m in match:
                if m != str(regex):
                    Globals.botCommands.append(m[:-1])

        botfile.close()

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

    def sendCommandInfo(self, User = None):
        msg = self.addMsgSpacing("Commands:")
        for i in range(1, len(Globals.botCommands)):
            if i > 1:
                msg += ", "
            msg += Globals.botCommands[i]
        if User != None:
            self.privateResponse(User, msg)
        else:
            self.channelResponse(msg)

    def connect(self):
        # attempt connection
        try:
            self.botSocket.connect((self.cfg.HOST, self.cfg.PORT));
            self.sendMsg("PASS oauth:{0}".format(self.cfg.OAUTH))
            self.sendMsg("NICK {0}".format(self.cfg.BOT_USERNAME))
            self.sendMsg("JOIN #{0}".format(self.cfg.CHANNEL))
            self.announceArrival()
            self.sendCommandInfo()
            self.botSocket.settimeout(10.0)

            return True
        except Exception as e:
            print("failed to connect!!! {0}".format(e))
            return False

    def addMsgSpacing(self, msg):
        numSpacesToAdd = Globals.maxLineCharCount - len(msg)
        tmp = msg
        while numSpacesToAdd > 0:
            tmp += "_"
            numSpacesToAdd -= 1
        return tmp

    def handleMsg(self):

        if not Globals.botQue.empty():
            response = Globals.getmsg()
            user = re.search(r"\w+", response).group()
            message = self.cfg.MSG_PATTERN.sub("", response).strip()

            Globals.printLockmsg("\n{0}: {1}".format(user, message))
            if (message.startswith("$Hello")):
                self.channelResponse("HI!!!")

            elif(message.startswith("$help")):
                self.sendCommandInfo(user)

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

            elif(message.startswith("$lineCharTest")):
                msg = ""
                for i in range(50):
                    msg += "0123456789"
                self.channelResponse(msg)

            elif (message.startswith("$topGames")):
                try:
                    url = "https://api.twitch.tv/helix/games/top"
                    req = requests.get(url, headers={'Client-ID': self.cfg.CLIENT_ID})
                    data = req.json()['data']
                    gameRank = 1
                    for dict in data:
                        name = self.addMsgSpacing(str(gameRank)+": Name: "+dict.get("name")+" ")
                        id = self.addMsgSpacing("ID: "+dict.get("id")+" ")
                        boxartUrl = self.addMsgSpacing("Box_Art_Url: "+dict.get("box_art_url")+" ")
                        boxartUrl = re.sub("{width}", "1920", boxartUrl)
                        boxartUrl = re.sub("{height}", "1080", boxartUrl)
                        self.privateResponse(user, name+id+boxartUrl)
                        gameRank += 1
                except Exception as e:
                    Globals.printLockmsg(e)

            elif (message.startswith("$Game")):
                try:
                    gameName = message[re.search(r"\s\w+", message).start()+1:]
                    url = "https://api.twitch.tv/helix/games?name="+gameName
                    req = requests.get(url, headers={'Client-ID': self.cfg.CLIENT_ID})
                    data = req.json()['data']
                    for dict in data:
                        name = self.addMsgSpacing("Name: " + dict.get("name") + " ")
                        id = self.addMsgSpacing("ID: " + dict.get("id") + " ")
                        boxartUrl = self.addMsgSpacing("Box_Art_Url: " + dict.get("box_art_url") + " ")
                        boxartUrl = re.sub("{width}", "1920", boxartUrl)
                        boxartUrl = re.sub("{height}", "1080", boxartUrl)
                        self.privateResponse(user, name + id + boxartUrl)
                except Exception as e:
                    Globals.printLockmsg(e)

        with Globals.tLock:
            Globals.threadCount -= 1
