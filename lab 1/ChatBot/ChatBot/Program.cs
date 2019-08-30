using System;
using System.Text;
using System.IO;
using System.Net;
using System.Net.Sockets;

//Host : "irc.chat.twitch.tv"
//Port : 6667
//pass : w74fi7jcegv41r2b2x25ktidpyb7vq
//Nick : bFriend
//Join : 1

public struct serverCred
{
    public string HOST;
    public int PORT;
    public string OAUTH;
    public string BOT_USERNAME;
    public string CHANNEL;
}

class Program
{
    //TRY USING IRC
    public string msgEnd = "\\r\\n";
    /*public static void ConnectSocket(Socket s, serverCred cfg)
    {
        IPHostEntry hostEntry = null;

        hostEntry = Dns.GetHostEntry(cfg.HOST);
        foreach (IPAddress address in hostEntry.AddressList)
        {
            IPEndPoint iPEnd = new IPEndPoint(address, cfg.PORT);
            Console.WriteLine("Address:{0}\nPort:{1}", iPEnd.Address.ToString(), iPEnd.Port.ToString());
            Socket tempS
                = new Socket(iPEnd.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
            if (tempS.Connected)
            {
                s = tempS;
                break;
            }
        }
        if (s == null)
            Console.WriteLine("failed to connect");
    }

    public static void sendMsg(Socket s, string msg)
    {
        s.Send(encodeString(msg));
    }

    private static byte[] encodeString(string s)
    {
        return Encoding.UTF8.GetBytes(s);
    }

    private static string decodeMsg(Decoder decoder, byte[] msgData)
    {
        int charCount = decoder.GetCharCount(msgData, 0, msgData.Length);
        Char[] chars = new Char[charCount];
        decoder.GetChars(msgData, 0, charCount, chars, 0);

        return chars.ToString();
    }

    private void connectToHost(Socket s, serverCred cfg)
    {
        string Pass = "PASS " + cfg.OAUTH + msgEnd;
        string Nick = "NICK " + cfg.BOT_USERNAME + msgEnd;
        string Join = "JOIN " + cfg.CHANNEL + msgEnd;

        sendMsg(s, Pass);
        sendMsg(s, Nick);
        sendMsg(s, Join);
    }

    public static Socket botSocket = null;
    public static serverCred cfg;
    public static byte[] buffer = new byte[2048];
    public static Decoder utf8Decoder;
    static void Main(string[] args)
    {
        cfg = new serverCred();
        cfg.HOST            = "irc.chat.twitch.tv";
        cfg.PORT            = 6667;
        cfg.OAUTH           = "w74fi7jcegv41r2b2x25ktidpyb7vq";
        cfg.BOT_USERNAME    = "bFriend";
        cfg.CHANNEL         = "nilkin1";

        Console.WriteLine(cfg);

        ConnectSocket(botSocket, cfg);
        utf8Decoder = Encoding.UTF8.GetDecoder();

        if (botSocket != null && botSocket.Connected)
        {
            Console.WriteLine("Connected to server");
            while (botSocket.Connected)
            {
                botSocket.Listen(1);
                botSocket.Receive(buffer);
                string msg = decodeMsg(utf8Decoder, buffer);
                if (msg == "PING")
                {
                    sendMsg(botSocket, "PONG");
                }
                else
                {
                    Console.WriteLine("got : {0}", msg);
                }
            }
        }
        else
            Console.WriteLine("Couldnt Connect or lost Connection");

        Console.WriteLine("Fin");
    }*/

    public class botClient
    {
        public string Name;
        private string Channel;

        private TcpClient tcpClient;
        private StreamReader input;
        private StreamWriter output;

        public botClient(string userName, string passwrd, string ip, string channel, int port)
        {
            this.Name = userName;
            this.Channel = channel;

            tcpClient = new TcpClient(ip, port);
            input = new StreamReader(tcpClient.GetStream(), Encoding.UTF8);
            output = new StreamWriter(tcpClient.GetStream(), Encoding.UTF8);

            try
            {
                sendMessage("PASS {0}\r\n", passwrd);
                sendMessage("NICK {0}\r\n", userName);
                sendMessage("JOIN {0}\r\n", Channel);
                output.Flush();
            }
            catch (Exception e)
            {
                Console.WriteLine("Establishing connection failure: \n\t{0}" +
                    "\n\tUser: {1}\n\tPass: {2}\n\tIP: {3}\n\tPort: {4}\n\tChannel: {5}"
                    ,e.Message, Name, passwrd, ip, port, channel);
            }
        }
        public bool getConnected()
        {
            return tcpClient.Connected;
        }
        public void sendMessage(string format, params object[] arg)
        {
            try
            {
                output.WriteLine(format, arg);
                output.Flush();
            }
            catch(Exception e)
            {
                Console.WriteLine("Sending message failure: \n\t{0}", e.Message);
            }
        }
        public string recieveMessage()
        {
            try
            {
                return input.ReadLine();
            }
            catch(Exception e)
            {
                return "Failed to read Message: \n\tException: " + e.Message;
            }
        }
        public void pingResponse()
        {
            sendMessage("PONG\r\n");
        }
    }

    static void Main(string[] args)
    {

        serverCred cfg = new serverCred();
        cfg.HOST = "irc.chat.twitch.tv";
        cfg.PORT = 6667;
        cfg.OAUTH = "w74fi7jcegv41r2b2x25ktidpyb7vq";
        cfg.BOT_USERNAME = "bFriend";
        cfg.CHANNEL = "nilkin1";

        botClient bFriend = new botClient(cfg.BOT_USERNAME, cfg.OAUTH, cfg.HOST, cfg.CHANNEL, cfg.PORT);
        string incomingMsg = "";

        while(bFriend.getConnected())
        {
            try
            {
                Console.WriteLine("Connected");
                incomingMsg = bFriend.recieveMessage();
                Console.WriteLine("Got: {0}", incomingMsg);
                if (incomingMsg.StartsWith("PING"))
                    bFriend.pingResponse();
            }
            catch(Exception e)
            {
                Console.WriteLine("Got Exception: \n\t{0}", e.Message);
                break;
            }
        }
        Console.WriteLine("Fin!");
    }
}