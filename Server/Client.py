import socket
import select
import errno
import sys
import re
from datetime import datetime
import time
import argparse



class IRCBot(object):



    def __init__(self, ip = "127.0.0.1", user = "Bot", name = "Bot", nick = "Bot", channel = ""):
        self.ip = ip
        self.port = 6667
        self.nickname = nick
        self.name = name
        self.user = user
        self.channel = channel
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rec_buffer = ""
        self.line_regex = re.compile(r"\r?\n")
        self.test = True



    def connect(self):
        self.socket.connect((self.ip, self.port))
        self.socket.setblocking(False)
        self.send_msg("USER " + self.user + " " + self.user + " " + self.user + " :" + self.name)
        self.send_msg("NICK " + self.nickname)
        if (self.channel != ""):
            self.send_msg("JOIN #" + self.channel)

    def send_msg(self, msg):

        print(">>> " + msg)
        self.socket.send((msg + "\r\n").encode())

    def recieve(self):
        try:
            self.rec_buffer += self.socket.recv(1000).decode()
            #print(self.rec_buffer)

        except IOError as e:
                # This is normal on non blocking connections - when there are no incoming data error is going to be raised
                # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
                # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
                # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()


    def buffer_empty(self):
        if(self.rec_buffer == ""):
            return True

    def parse_buffer(self):
        lines = self.line_regex.split(self.rec_buffer)
        self.rec_buffer = lines[-1]
        lines = lines[0:-1]
        for line in lines:

            if (not line):
                continue

            line_split = {}
            command_args = {}
            msg = ""

            print("<<< " + line)

            if (line.find(":") != -1):
                line_split = line.strip(":").split(":")

                command_args = line_split[0].strip(" ").split(" ")

                if (len(line_split) > 1):
                    msg = line_split[-1]

            #print(str(command_args) + " > " + msg)

            self.handle_command(command_args,msg)




    def handle_command(self, args, msg):
        command = ""

        if (len(args) == 1):
            command = args[0]
        elif (len(args) >= 2):
            command = args[1]
        else:
            return

        def pong_handler():
            self.send_msg("PONG :" + msg)

        def privmsg_handler():
            msg_from = args[0].split("!")[0]
            if(re.match("#", args[2])):
                print(msg_from + "> " + args[2] + ": " + msg)

                if (re.match("!", msg)):

                    def bot_time():
                        self.send_msg("PRIVMSG " + args[2] + " :" + str(datetime.time(datetime.now())))

                    def bot_date():
                        self.send_msg("PRIVMSG " + args[2] + " :" + str(datetime.date(datetime.now())))

                    bot_commands = {
                        "!time": bot_time,
                        "!date": bot_date
                    }

                    try:
                        bot_commands[msg]()
                    except KeyError:
                        print("not a valid command")

            else:
                print(msg_from + ": " + msg)
                self.send_msg("PRIVMSG " + msg_from + " :fuck off you stupid cunt")

        #print(command)
        command_handlers = {
            "PING": pong_handler,
            "PRIVMSG": privmsg_handler
        }

        try:
            command_handlers[command]()
        except KeyError:
            print("no handler for command/ reply number")


    def run(self):
        self.connect()
        while True:
            self.recieve()
            if(not self.buffer_empty()):
                self.parse_buffer()

def main():

    parser = argparse.ArgumentParser(description = "A bot for the irc protocol")
    parser.add_argument('--server', help="server to connect to (default = '127.0.0.1')", default = "127.0.0.1")
    parser.add_argument('--nick', help="nickname to use on the server (default = 'Bot')", default = "Bot")
    parser.add_argument('--user', help="username to use on the server (default = 'Bot')", default = "Bot")
    parser.add_argument('--name', help="real name to use on the server (default = 'Bot')", default = "Bot")
    parser.add_argument('--channel', help="channel to connect to on the server (none by default)", default = "")

    print("\n ___ ___  ___ ___      _ ")
    print("|_ _| _ \\/ __| _ ) ___| |_ ")
    print(" | ||   / (__| _ \\/ _ \\  _|")
    print("|___|_|_\\\\___|___/\\___/\\__|\n")

    args = parser.parse_args()

    bot = IRCBot(ip = args.server, user = args.user, name = args.name, nick = args.nick, channel = args.channel)
    bot.run()

if __name__ == "__main__":
    main()
