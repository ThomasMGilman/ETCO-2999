import re
import socket
import time

HOST = "irc.chat.twitch.tv"
PORT = 6667
OAUTH = "w74fi7jcegv41r2b2x25ktidpyb7vq"
USERNAME = "bFriend"
CHANNEL = "nilkin1"

class chatConnection:
    HOST = None
    PORT = None
    OAUTH = None
    BOT_USERNAME = None
    CHANNEL = None
    MSG_PATTERN = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

    def __init__(self, host, port, ps, nick, join):
        self.HOST = host
        self.PORT = port
        self.OAUTH = ps
        self.BOT_USERNAME = nick
        self.CHANNEL = join

class bot:
    botSocket = None
    cfg = None
    def __init__(self, cfg):
        # create socket
        self.botSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cfg = cfg

    def sendMsg(self, msg):
        self.botSocket.send((msg+"\r\n").encode('utf-8'))

    def recv(self):
        return self.botSocket.recv(2048).decode("utf-8")

    def keepAlive(self):
        self.sendMsg("PONG :tmi.twitch.tv")

    def connect(self):
        # attempt connection
        try:
            self.botSocket.connect((self.cfg.HOST, self.cfg.PORT));
            self.sendMsg("PASS oauth:{0}".format(self.cfg.OAUTH))
            self.sendMsg("NICK {0}".format(self.cfg.BOT_USERNAME))
            self.sendMsg("JOIN #{0}".format(self.cfg.CHANNEL))
            print("connected")
            return True
        except Exception as e:
            print("failed to connect!!! {0}".format(e))
            return False

    def announceArrival(self):
        self.sendMsg("PRIVMSG #{0} :{1} has arrived!!!".format(self.cfg.CHANNEL, self.cfg.BOT_USERNAME))
        self.sendMsg("/mod {0}".format(self.cfg.CHANNEL))

    def channelResponse(self, msg):
        self.sendMsg("PRIVMSG #{0} :{1}".format(self.cfg.CHANNEL, msg))

def main():
    cfg = chatConnection(HOST, PORT, OAUTH, USERNAME, CHANNEL)

    try:
        #create bot and attempt connection
        botSocket = bot(cfg)
        connected = botSocket.connect()

        while connected:
            response = botSocket.recv()
            print(response)
            if response.startswith("PING"):
                botSocket.keepAlive()
            else:
                #Get message passed from users
                user = re.search(r"\w+", response).group(0)
                message = cfg.MSG_PATTERN.sub("", response).strip()

                print("{0}: {1}".format(user, message))
                if(message.startswith("$Hello")):
                    botSocket.channelResponse("HI!!!")
                #elif(message.startswith("$ColorTxt")):
                #    botSocket.sendMsg("/me this is color text!!!")
                #elif(message.startswith("$ByeFriend")):
                #   botSocket.sendMsg("/disconnect")
            time.sleep(1)

    finally:
        print("exiting")

main()