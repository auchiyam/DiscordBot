import discord

@staticmethod
def pop_command(st, command):
    return st[len(command)+1:len(st)]
