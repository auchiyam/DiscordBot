import time, sched
from datetime import datetime, timedelta
from enum import  Enum
import discord
import botutil

class Reminder:
    class Repeat(Enum):
        daily = 1
        weekly = 2
        monthly = 3
        yearly = 4
        never = 5

    def __init__(self, channel, server, command=list(), note="default text", time=datetime.now(), repeat=5, users=["everyone"], message=""):
        self.time = time
        self.repeat = 5
        self.users = users
        self.note = note
        self.server = server
        self.channel = channel
        self.error = ""

        if len(command) > 0:
        
            #parse the command .remind "note" time [repeat] [user]
            #returns error statement; an emptry string if successful
            def parse(command):
                cmd = command
                note = ""
                #get note from command
                if cmd[0].startswith('"'):
                    if cmd[0].endswith('"'):
                        note += cmd[0][1:len(cmd[0]) - 1]
                        cmd.pop(0)
                    else:
                        note += cmd[0][1:] + " "
                        cmd.pop(0)
                        while (len(cmd) > 0 and not cmd[0].endswith('"')):
                            note += cmd[0]+ " "
                            cmd.pop(0)
                        if len(cmd) > 0:
                            note += cmd[0][0:len(cmd[0]) - 1]
                            cmd.pop(0)
                        else:
                            return "Invalid input.  Note didn't end with quotes."
                
                else:
                    return "Invalid input.  Note is not enclosed in quotes."

                print("%s %s" % (cmd[0], cmd[1]))
                #get time from command
                if len(cmd) > 0:
                    if get_date(cmd[0]) != 0:
                        self.time = get_date(cmd[0])
                        cmd.pop(0)
                        print(self.time)
                    if len(cmd) > 0 and get_time(cmd[0]) != 0:
                        t = get_time(cmd[0])
                        self.time = datetime(time.year, time.month, time.day, t.hour, t.minute, t.second)
                        cmd.pop(0)
                        print(self.time)
                        
                #checks if time is valid
                if self.time - datetime.now() < timedelta(microseconds=0):
                    return "Invalid time input."
            
                #get repeat from command
                if len(cmd) > 0:
                    if get_repeat(cmd[0]) != 0:
                        repeat = get_repeat(cmd[0])
                        cmd.pop(0)
                    else:
                        repeat = 5
                
                #get users from command
                self.users = get_users()

                self.note = note
                self.repeat = repeat
                return ""

            def get_repeat(command):
                if (command == "daily"):
                    return 1
                elif (command == "weekly"):
                    return 2
                elif (command == "monthly"):
                    return 3
                elif (command == "yearly"):
                    return 4
                elif (command == "never"):
                    return 5
                else:
                    return 0

            def get_date(command):
                t = 0
                try:
                    t = datetime.strptime(command, '%Y-%m-%d')
                    return t
                except ValueError:
                    try:
                        t = datetime.strptime(command, '%m/%d/%Y')
                        return t
                    except ValueError:
                        try:
                            t = datetime.strptime(command, '%m-%d')
                            return t
                        except ValueError:
                            try:
                                t = datetime.strptime(command, '%m/%d')
                                return t
                            except ValueError:
                                return 0
                
            def get_time(command):
                try:
                    t = datetime.strptime(command.upper(), '%HAM')
                    return t
                except ValueError:
                    try:
                        t = datetime.strptime(command.upper(), '%HPM') + timedelta(hours=12)
                        return t
                    except ValueError:
                        try:
                            t = datetime.strptime(command, '%H:%M')
                            return t
                        except ValueError:
                            try:
                                t = datetime.strptime(command.upper(), '%H:%MAM')
                                return t
                            except ValueError:
                                try:
                                    t = datetime.strptime(command, "%H")
                                    return t
                                except ValueError:
                                    try:
                                        t = datetime.strptime(command.upper(), '%H:%MPM') + timedelta(hours=12)
                                        return t
                                    except ValueError:
                                        return 0
                    

            def get_users():
                u = set()
                if message.mention_everyone:
                    u.update(self.server.members)
                if len(message.role_mentions) > 0:
                    u.update(message.role_mentions)
                if len(message.mentions) > 0:
                    u.update(message.mentions)
                if len(u) == 0:
                    u = {message.author}
                return u
            
            self.error = parse(command)
