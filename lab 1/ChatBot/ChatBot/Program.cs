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
    
    public static string msgEnd = "\r\n";

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
            input = new StreamReader(tcpClient.GetStream());//, Encoding.UTF8);
            output = new StreamWriter(tcpClient.GetStream());//, Encoding.UTF8);

            try
            {

                sendMessage("PASS oauth: {0}", passwrd);
                sendMessage("NICK {0}", userName);
                sendMessage("JOIN #{0}", Channel);

                if(tcpClient.Connected)
                    Console.WriteLine("Connected");
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
                output.WriteLine(format+msgEnd, arg);
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
            sendMessage("PONG :tmi.twitch.tv");
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

        while(bFriend.getConnected())
        {
            try
            {
                string incomingMsg = bFriend.recieveMessage();
                if(incomingMsg != null)
                {
                    Console.WriteLine("Got: {0}", incomingMsg);
                    if (incomingMsg.StartsWith("PING"))
                        bFriend.pingResponse();
                }
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