import time, sched
from datetime import datetime, timedelta
from enum import  Enum
import discord
import botutil
from database import Database
import database
import pymysql

class InvalidReminder(Exception):
    def __init__(self, r):
        self.message = "No such reminder exists"
        self.reminder = r

class Reminder:
    class Repeat(Enum):
        daily = 1
        weekly = 2
        monthly = 3
        yearly = 4
        never = 5

    def __init__(self, channel, server, command=list(), note="default text", time=datetime.now(), repeat=5, users=["everyone"], message=""):
        if isinstance(time, str):
            self.time = datetime.strptime("%Y-%m-%d %H:%M:%S", time)
        else:
            self.time = time
        self.repeat = 5
        self.users = users
        self.note = note
        if isinstance(server, str):
            self.server = server
        else:
            self.server = server.id
        if isinstance(channel, str):
            self.channel = channel
        else:
            self.channel = channel.id
        self.deleted = False
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

                #get time from command
                if len(cmd) > 0:
                    if get_date(cmd[0]) != 0:
                        self.time = get_date(cmd[0])
                        cmd.pop(0)
                    if len(cmd) > 0 and get_time(cmd[0]) != 0:
                        t = get_time(cmd[0])
                        self.time = datetime(time.year, time.month, time.day, t.hour, t.minute, t.second)
                        cmd.pop(0)
                        
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
                    u.update(message.server.members)
                if len(message.role_mentions) > 0:
                    u.update(message.role_mentions)
                if len(message.mentions) > 0:
                    u.update(message.mentions)
                if len(u) == 0:
                    u = {message.author}
                return u
            
            self.error = parse(command)
        else:
            self.update_time()
    
    def __str__(self):
        r = self
        try:
            rid = r.get_id()
            return "Note: %s\nTime: %s\nRepeat: %s\nUsers: %s\nChannel: %s" % (r.note, r.time, r.repeat, r.users, r.channel)
        except InvalidReminder:
            self.error = "invalid reminder"
            return "This reminder does not exist in the database"

    #inserts the reminder to the database
    def insert_reminder(self):
        with Database() as d:
            if isinstance(self.channel, str):
                did = d.select("reminder", ["max(id)"], "channel='%s'" % self.channel)[0]["max(id)"]
            else:
                did = d.select("reminder", ["max(id)"], "channel='%s'" % self.channel.id)[0]["max(id)"]
            if isinstance(did, str):
                rid = int(did) + 1
            else:
                rid = 0
            n = d.escape_characters(self.note, "'")
            try:
                oid = self.get_id()
                self.error = "duplicate reminder"
                return "A reminder with same note and time exists!\nPlease edit the existing reminder using the id [__%s__].\nFor more information on editing a reminder, type `%shelp remind` or `%sremind edit.`"\
                    % (oid, self.prefix[0], self.prefix[0])
            except InvalidReminder:
                pass
            
            while True:
                try:
                    d.insert("reminder", [rid, n, self.time, self.repeat, self.channel], ["id", "note", "time", "reuse", "channel"])
                    break
                except pymysql.err.IntegrityError:
                    rid += 1
            for u in self.users:
                if not (bool(self.users) and all([isinstance(i, str) for i in self.users])):
                    d.insert("users_highlighted_for_reminder", [rid, u.name, self.channel], ["id", "user", "channel"])
                else:
                    d.insert("users_highlighted_for_reminder", [rid, u, self.channel], ["id", "user", "channel"])
            d.update_id("reminder", self.server, rid + 1)
            u = list()
            for k in self.users:
                if isinstance(k, str):
                    u.append(k)
                else:
                    u.append(k.name)
            return ("The following reminder has been added!:\nNote: %s\nTime: %s\nRepeat: %s\nUsers: %s" % (self.note, self.time, self.repeat, u))

    #updates this reminder's database input to the new reminder in args
    def update_reminder(self, new_reminder):
        with Database() as d:
            rid = self.get_id()
            d.update("reminder", ["note='%s'" % new_reminder.note, "time='%s'" % new_reminder.time, "reuse='%s'" % new_reminder.repeat, "channel='%s'" % new_reminder.channel.id], "channel='%s' AND id='%s'" % (new_reminder.channel.id, rid))
            d.delete("users_highlighted_for_reminder", "id='%s' AND channel='%s'" % (rid, self.channel))
            for u in self.users:
                if not (bool(self.users) and all([isinstance(i, str) for i in self.users])):
                    d.insert("users_highlighted_for_reminder", [rid, u.name, self.channel])
                else:
                    d.insert("users_highlighted_for_reminder", [rid, u, self.channel])

    def update_time(self):
        old = self
        while self.time - datetime.now() < timedelta(minutes=10):
            if self.repeat == 5:
                break
            def get_time(time):
                if self.repeat == 1:
                    return time + timedelta(days=1)
                if self.repeat == 2:
                    return time + timedelta(days=7)
                if self.repeat == 3:
                    return time + timedelta(days=self.get_dates(time))
                if self.repeat == 4:
                    next_year = time + timedelta(days=365)
                    if is_leap_year(next_year) and next_year >= datetime(year=next_year.year, month=2, day=29):
                        return next_year + timedelta(days=1)
                    return next_year
                def is_leap_year(self, t):
                    year = t.year
                    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0
            self.time = get_time(self.time)
        if self.repeat != 5:
            old.update_reminder(self)
        else:
            if self.time - datetime.now() < timedelta(minutes=10):
                self.delete_reminder()

    def delete_reminder(self):
        with Database() as d:
            rid = self.get_id()
            d.delete("reminder", "id='%s' AND channel='%s'" % (rid, self.channel))
            d.delete("users_highlighted_for_reminder", "id='%s' AND channel='%s'" % (rid, self.channel))
            self.deleted = True

    def get_id(self):
        with Database() as d:
            try:
                return d.select("reminder", ["id"], "channel='%s' AND note='%s' AND time='%s'" % (self.channel, d.escape_characters(self.note, "'"), self.time))[0]['id']
            except:
                raise InvalidReminder(self)