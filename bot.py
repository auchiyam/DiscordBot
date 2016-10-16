import discord
import asyncio
from reminder import Reminder
import botutil
from database import Database
from eventhandler import EventHandler
import json
from io import StringIO



class Bot:

    ##########global variables##########
    #connect to Discord
    client = discord.Client()

    #prefix for command
    prefix = [".","!", "miku, "]

    #events to react to
    event = EventHandler(client, prefix)
    ##########global variables##########

    def __init__(self, token):
        Bot.client.run(token)

    #preloading on start up
    @client.event
    async def on_ready():
        print('Logged in as')
        print(Bot.client.user.name)
        print(Bot.client.user.id)
        print('------')
    
        with Database() as d:
        
            for server in Bot.client.servers:
                #Makes sure all servers have the id database
                if (len(d.select("ids", ["server"], operator="server='%s'" % server.id)) == 0):
                    d.insert("ids", [server.id, 0,0,0,0])

                #Adds all reminders back to alarm
                for channel in server.channels:
        
                    l = d.select("reminder", ["*"], "channel='%s'" % (channel.id))
                    for row in l:
                        r = Reminder(channel, server, note=row['note'], time=row['time'], repeat=row['reuse'])
                        if r.deleted:
                            continue
                        rid = r.get_id()
                        us = [i["user"] for i in d.select_joined("users_highlighted_for_reminder", "reminder",
                        ["users_highlighted_for_reminder.id=reminder.id", "users_highlighted_for_reminder.channel=reminder.channel"],
                        ["users_highlighted_for_reminder.user"],
                        "reminder.id='%s' AND reminder.channel='%s'" % (rid, r.channel))]
                        r.users = us
                        err = Bot.event.create_new_alarm(r)
        print('------')
        print('MikuBot is ready to go!')

    @client.event
    async def on_server_join(server):
        print("Miku joined %s!" % server.name)
        with Database() as d:
            if (len(d.select("ids", ["server"], operator="server='%s'" % server.id)) == 0):
                d.insert("ids", [server.id, 0,0,0,0])

    #handling message received
    @client.event
    async def on_message(message):
        for p in Bot.prefix:
            if message.content.lower().startswith(p):
                await Bot.switch(message, p)
                break

    #figures out what command to use
    @staticmethod
    async def switch(m, p):
        command = m.content.lower()[len(p):len(m.content)].split()
        #help
        if (len(command) > 0):
            c = command[0]
            command.pop(0)
            if c == "help":
                h = Bot.display_help(command)
                await Bot.client.send_message(m.author, h)

            #reminder
            elif c == "remind":
                await Bot.reminder(command, m.channel, m.server, m)
        
            elif c == "beatmap":
                await Bot.client.send_message(m.channel, "currently wip.")
        
            elif c == "anime":
                await Bot.client.send_message(m.channel, "currently wip.")
        
            elif c == "pixiv":
                await Bot.client.send_message(m.channel, "currently wip.")
        
            elif c == "meme":
                await Bot.client.send_message(m.channel, "currently wip.")
        
            elif c == "quote":
                await Bot.client.send_message(m.channel, "currently wip.")
        
            elif c == "music":
                await Bot.client.send_message(m.channel, "currently wip.")
        
            elif c == "birthday":
                await Bot.client.send_message(m.channel, "currently wip.")
        
            elif c == "timezone":
                await Bot.client.send_message(m.channel, "currently wip.")
        
            elif c == "feature":
                await Bot.client.send_message(m.channel, "currently wip.")
        
            elif c == "quit":
                await Bot.close_bot(m.author.id)
            
            elif c == "prefix":
                await Bot.client.send_message(m.channel, "currently wip.")

            elif c == "id":
                await Bot.client.send_message(m.channel, m.author.id)
    
            else:
                await Bot.client.send_message(m.channel, "The command '%s%s' doesn't exist!'" % (Bot.prefix[0]))

    #command to turn off Miku
    @staticmethod
    async def close_bot(user):
        if (user == '93062570772021248'):
            await Bot.client.logout()
            await Bot.client.close()
            print("Miku has successfully logged out")

    @staticmethod
    def display_help(command):
        h = ""
        legend = '**legends**\ncommands in "quotes" must be inside quotes to work.\ncommands in [brackets] are optional and can be left out.\nEverything in (parenthesis) are arguments.  You must fill them out appropriately.\n**ORDER MATTERS!**\n'
        if len(command) == 0:
            h += "Here's the list for all the commands, including the wip:\n"
            h += "---\n"
            h += "**WIP**\n"
            h += "---\n"
            h += "__anime__: returns information about the currently airing anime\n"
            h += "__beatmap__: returns information about the beatmap provided.\n"
            h += "__birthday__: stores the birthdays of the users in this server\n"
            h += "__changelog__: list of recent changes that was made to this bot."
            h += "__feature request__: database of feature requests to improve this bot!\n"
            h += "__meme__: controls the meme database in the server\n"
            h += "__music__: save and play music shared in the server\n"
            h += "__pictures__: save and displays pictures in the server\n"
            h += "__pixiv__: provides couple of functions related to pixiv\n"
            h += "__prefix__: customizes the prefix you can use for this bot.  Default is '.'\n"
            h += "__quote__: stores quotes that has been said by a member\n"
            h += "__remind__: Sets a reminder that will go off on a certain date\n"
            h += "__timezone__: sets timezone for each users for convenience\n"
            h += "---\n"
            h += "**WORKING**\n"
            h += "---\n"
            h += "__help__: the command you are using right now! Provides list of all commands\n"
            h += "---\n"
            h += "For more information about each commands, type '%shelp [command]'." % (Bot.prefix[0])

        else:
            if command[0] == "anime":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "beatmap":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "birthday":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "feature":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "meme":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "music":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "pictures":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "pixiv":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "quote":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "remind":
                command.pop(0)
                if len(command) == 0:
                    h += "**remind**\n"
                    h += "---\n"
                    h += '__add__: ("note" time [repeat] [users]) adds a reminder.  Can be shortened to \'-a\'\n'
                    h += '__list__: () shows all the reminders in the channel.   Can be shortened to \'-l\'\n'
                    h += '__remove__: () removes the reminder  Can be shortened to \'-r\'\n'
                    h += '__edit__: () edits an existing reminder  Can be shortened to \'-e\'\n'
                    h += '__optout__: () removes yourself from the list of users highlighted on the reminder so you will not be highlighted from the reminder  Can be shortened to \'-o\'\n'
                    h += '__describe__: () describes a reminder in detail  Can be shortened to \'-d\'\n'
                    h += "---\n"
                    h += legend
                    h += "---\n"
                    h += "If you're still unsure of what to type for each arguments, type '%shelp remind [command]' for even more info!" % (Bot.prefix[0])
                else:
                    if command[0] == "add" or command[0] == "-a":
                        h += "**remind add**\n"
                        h += "---\n"
                        h += '__"note"__:\n Write what you want the reminder to say.  Avoid highlighting someone in notes because it causes some issues and it\'ll only show 15 digit numbers, not names. _ex: "test day", "owc match at saturday_"\n\n'
                        h += '__time__:\n The date and time you want the reminder to set off on. The supported format for date includes "yyyy-mm-dd", "mm/dd/yyyy", "mm/dd", and "mm-dd".  The supported format for the time is "hh:mmAMorPM", "hh:mm" (24 hours), "hhAMorPM", and "hh" (24 hours). Place a space between the date and time, but not anywhere else! (am/pm does not need any space!). _ex: 11-15-2019 3:09PM_\n\n'
                        h += '__[repeat]__:\n Repeat determines if this reminder is going to set off again at later time.  There are 5 options for repeat: "daily", "weekly", "monthly", "yearly", and "**never**".  As the repeat name suggests, they determine if it plays again every day, week, month, or year respectively.  **never** is the default value if no repeat was given.\n\n'
                        h += '__[users]__:\n list of users to highlight when the time comes.  You must highlight the person properly, like "%s" or the reminder will not read the users.  Important to note that if you highlight someone in the "__note__" argument, they will also be added to the list of mentions, which might cause issues.  Your own name is the default value if no users were given.\n' % (Bot.client.user.mention)
                        h += "---\n"
                    elif command[0] == "list" or command[0] == "-l":
                        h += "This command is currently wip.  Check back later!"
                    elif command[0] == "remove" or command[0] == "-r":
                        h += "This command is currently wip.  Check back later!"
                    elif command[0] == "edit" or command[0] == "-e":
                        h += "This command is currently wip.  Check back later!"
                    elif command[0] == "optout" or command[0] == "-o":
                        h += "This command is currently wip.  Check back later!"
                    elif command[0] == "describe" or command[0] == "-d":
                        h += "This command is currently wip.  Check back later!"
                    else:
                        h += "Could not find the command you were looking for.  Are you sure you typed the command correctly?\n%s" % (display_help(["remind"]))
                    
            elif command[0] == "timezone":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "prefix":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            elif command[0] == "changelog":
                command.pop(0)
                h += "This command is currently wip.  Check back later!"
            else:
                h += "Could not find the command you were looking for.  Are you sure you typed the command correctly?\n%s" % (display_help([]))
        return h

    @staticmethod
    async def reminder(command, channel, server, message):
        if (len(command) > 0):
            c = command[0]
            command.pop(0)
            if c == "add" or c == "-a":
                await Bot.add_reminder(command, channel, server, message)
            elif c == "list" or c == "-l":
                #self.list_reminder(command)
                await Bot.client.send_message("Currently wip")
            elif c == "remove" or c == "-r":
                await Bot.client.send_message("Currently wip")
            elif c == "edit" or c == "-e":
                await Bot.client.send_message("Currently wip")
            elif c == "optout" or c == "-o":
                await Bot.client.send_message("Currently wip")
            elif c == "describe" or c == "-d":
                await Bot.client.send_message("Currently wip")
            else:
                h = Bot.display_help(["remind"])
                await Bot.client.send_message(m.channel, "That remind command doesn't exist!\n%s" % (h))
        else:
            h = Bot.display_help(["remind"])
            await Bot.client.send_message(m.channel, "That remind command doesn't exist!\n%s" % (h))  
    
    #add "note" time [repeat] [users]
    @staticmethod
    async def add_reminder(command, channel, server, message):
        r = Reminder(channel, server, command=command, message=message)
        if (len(r.error) == 0):
            err = Bot.event.create_new_alarm(r)
            if len(err) == 0:
                with Database() as d:
                    n = d.escape_characters(r.note, "'")
                    err = r.insert_reminder()
                    
                    await Bot.client.send_message(channel, err)
            else:
                h = Bot.display_help(["remind"])
                await Bot.client.send_message(channel, err + "\n")
        else:
            h = Bot.display_help(["remind", "add"])
            await Bot.client.send_message(channel, r.error + "\n")

    '''
    #list ["note"] [time1] [time2] [users]
    @staticmethod
    async def list_reminder(command):
        r = Reminder.list_reminders(command)
         
    @staticmethod
    async def remove_reminder(command):
    
    @staticmethod
    async def edit_reminder(command):
    
    @staticmethod
    async def optout_reminder(command):

    @staticmethod
    async def describe_reminder(command):
    '''