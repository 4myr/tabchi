from telethon import TelegramClient, events

from telethon.sync import TelegramClient
from telethon import functions, types, errors

import config
import redis
import sys, os, asyncio

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Handle multiple instances without any duplicate
# instance = input('Enter your instance name [example: amyr]: ') if len(sys.argv) < 2 else sys.argv[1]
instance = "amyr"
instance_path = os.path.abspath("Sessions/{0}".format(instance))


# A simply function for showing errors
def client_has_error(error):
    print(colors.FAIL + "[Error]: " + colors.ENDC + error)

# Join redis variable name to instance name
def cnf(name):
    return "{0}_{1}".format(instance, name)


# Initialize Redis-Server
r = redis.Redis()
if not r.ping():
    client_has_error("Redis is not ready!")
    exit();

# Initilize variables
CRON_TIME = int( r.get( cnf("CRON_TIME") ) ) or ( 120 and r.set( cnf("CRON_TIME"), 120 ) and print("CRON_TIME has been set to default (120)") )
MAX_GROUPS = int( r.get( cnf("MAX_GROUPS") ) ) or ( 150 and r.set( cnf("MAX_GROUPS"), 150 ) and print("MAX_GROUPS has been set to default (150)") )
BOT_USER = r.get( cnf("BOT_USER") ) or None # configured BOT_USER will replace on adverstiment texts for {BOT_USER}

welcome_text = "------ WELCOME ------\n"
welcome_text += "Redis:         " + colors.OKGREEN + "is ok!" + colors.ENDC + "\n"
welcome_text += "CRON_TIME:     " + colors.UNDERLINE + str(CRON_TIME) + colors.ENDC + "\n" 
welcome_text += "MAX_GROUPS:    " + colors.UNDERLINE + str(MAX_GROUPS) + colors.ENDC + "\n" 
welcome_text += "BOT_USER:      " + colors.UNDERLINE + str(BOT_USER) + colors.ENDC + "\n\n" 
print(welcome_text)

# A simply function to making link for a user
def make_user_link(from_id, name):
    link = "[{}](tg://user?id={})".format(name, from_id)
    return link

# A simply function to handle and returning true from_id
def get_from_id(event_to_id):
    to_id = null
    if hasattr(event_to_id, 'chat_id'):
        to_id = event_to_id.chat_id
    elif hasattr(event_to_id, 'user_id'):
        to_id = event_to_id.user_id
    elif hasattr(event_to_id, 'channel_id'):
        to_id = event_to_id.channel_id

    return to_id

# Telethon client start
client = TelegramClient(instance_path, config.api_id, config.api_hash)
print("Bot({0}) is running...".format(instance))

# An event to handle new messages
@client.on(events.NewMessage)
async def newMessage(event):
    cmd_message = str(event.raw_text)
    cmd_params = cmd_message.split(' ')
    me = await client.get_me()

    # Stats
    if cmd_message == '!stats':
        dialogs = await client.get_dialogs()
        count_all = 0
        count_users = 0
        count_groups = 0
        count_channels = 0
        count_bots = 0
        for d in dialogs:
            count_all += 1
            if d.is_user:
                if d.entity.bot:
                    count_bots += 1
                else:
                    count_users += 1
            elif d.is_group:
                count_groups += 1
            elif d.is_channel:
                count_channels += 1

        response_text = "**My Stats**\n\nUsers: `{}`\nGroups: `{}`\nChannels: `{}`\nBots: `{}`\nAll: `{}`\n\n**RAM Usage: %{}**\n**CPU Usage: %{}**\n**Disk Usage: %{}**".format(count_users, count_groups, count_channels, count_bots, count_all, psutil.virtual_memory()[2], psutil.cpu_percent(), psutil.disk_usage('/')[3])
        await event.reply(response_text)

# Create cron event
def create_cron_event():    
    loop = asyncio.get_event_loop()
    cron_task = cron(2)
    task = loop.create_task(cron_task)
    loop.run_until_complete(task)

# All codes need cron write here
async def cron(time):
    while True:
        print("Task working!")
        await asyncio.sleep(time)

try:
    client.start()
    task = create_cron_event()
    client.run_until_disconnected()
except Exception as error:
    client_has_error(error)