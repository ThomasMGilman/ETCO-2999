from socket import *

class chatConnection:
    HOST = None
    PORT = None
    OAUTH = None
    BOT_USERNAME = None
    CHANNEL = None
    def __init__(self, host, port, ps, nick, join):
        self.HOST = host
        self.PORT = port
        self.OAUTH = ps
        self.BOT_USERNAME = nick
        self.CHANNEL = join


def main():

    localHost = 127001;
    cfg = chatConnection()

    try:
        botSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        botSocket.connect(

    finally:
        print("exiting")