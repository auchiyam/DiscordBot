import discord
import pymysql
import asyncio

#connect to sql database
connection = pymysql.connect(host='52.89.74.4',
                             port=3306,
                             user='koinuri',
                             password='592358803zDf',
                             db='commands',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

#connect to Discord
client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')
    

client.run('MjI3NjUxMzI4NDA1NTM2NzY5.CsJgDA.cNDzPyfXoIvOzf8X2zjt13kDFv8')
