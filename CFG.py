import re

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