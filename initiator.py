from bot import Bot
from database import Database
import sys
import discord
import logging
import asyncio

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

log = logging.getLogger('timer')
log.setLevel(logging.DEBUG)
hand = logging.FileHandler(filename='timer.log', encoding='utf-8', mode='w')
hand.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
log.addHandler(hand)

#Use this bot through command prompt.  The arguments are
#initiator.py bot_token IP_for_MySQL_database username_for_database password_for_the_username database_to_work_on
def initialize_database():
    with Database() as d:
        tables = [i['table_name'] for i in d.MySQL_commands("SELECT table_name from information_schema.tables WHERE table_schema = '%s' order by table_name asc;" % (Database.MySQL_db))]
        correct_tables = \
        {
            'ids':[ ('server','varchar(50)'), ('reminder', 'varchar(10)') ],
            'reminder':[ ('id', 'varchar(10)'), ('note', 'mediumtext'), ('time', 'datetime'), ('reuse', 'smallint(2) unsigned'), ('channel', 'varchar(50)') ],
            'users_highlighted_for_reminder':[ ('id', 'varchar(10)'), ('user', 'varchar(64)'), ('channel', 'varchar(50)') ]
        }

        primary_keys = \
        {
            'ids':[ 'server' ],
            'reminder':[ 'id', 'channel' ],
            'users_highlighted_for_reminder':[ 'id', 'channel', 'user' ]

        }
        count = d.MySQL_commands("SELECT count(*) from information_schema.tables WHERE table_schema = '%s';" % (Database.MySQL_db))[0]['count(*)']
        for key,value in correct_tables.items():
            if key in tables:
                result = [(i['Field'], i['Type']) for i in d.MySQL_commands("describe %s;" % (key))]
                check = value
                for col in check:
                    if col not in result:
                        if col[0] in [e for r in result for e in r]:
                            d.MySQL_commands("alter table %s change %s %s %s;" % (key, col[0], col[0], col[1]))
                        else:
                            d.MySQL_commands("alter table %s add %s %s;" % (key, col[0], col[1]))
                pk = "("
                for i in primary_keys[key]:
                    pk += '%s,' % (i)
                pk = pk[0:-1] + ")"
                try:
                    d.MySQL_commands("alter table %s drop primary key, add primary key %s;" % (key, pk))
                except:
                    d.MySQL_commands("alter table %s add primary key %s;" % (key, pk))

            else:                
                l = ["%s %s" % (i[0], i[1]) for i in correct_tables[key]]
                d.create_table(key, l)
                pk = "("
                for i in primary_keys[key]:
                    pk += '%s,' % (i)
                pk = pk[0:-1] + ")"
                d.MySQL_commands("alter table %s add primary key %s;" % (key, pk))

Database.MySQL_IP = sys.argv[2]
Database.MySQL_user = sys.argv[3]
Database.MySQL_pass = sys.argv[4]
Database.MySQL_db = sys.argv[5]

initialize_database()

Bot.client.loop.create_task(back())

b = Bot(sys.argv[1])

def back():
    count = 0
    while not Bot.client.is_closed:
        log.info("running for...%s" % count)
        count += 1
        await asyncio.sleep(60)