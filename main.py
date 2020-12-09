from telethon import TelegramClient, events

from telethon.sync import TelegramClient
from telethon import functions, types, errors

import config
import redis
import sys, os, asyncio, psutil, re

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
instance = input('Enter your instance name [example: amyr]: ') if len(sys.argv) < 2 else sys.argv[1]
# instance = "amyr"
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
CRON_TIME = r.get( cnf("CRON_TIME") ) or ( 120 and r.set( cnf("CRON_TIME"), 120 ) and print("CRON_TIME has been set to default (120)") )
JOIN_TIME = r.get( cnf("JOIN_TIME") ) or ( 200 and r.set( cnf("JOIN_TIME"), 200 ) and print("JOIN_TIME has been set to default (200)") )
MAX_GROUPS = r.get( cnf("MAX_GROUPS") ) or ( 150 and r.set( cnf("MAX_GROUPS"), 150 ) and print("MAX_GROUPS has been set to default (150)") )
BOT_USER = r.get( cnf("BOT_USER") ) or None # configured BOT_USER will replace on adverstiment texts for {BOT_USER}

CRON_TIME = int(CRON_TIME)
JOIN_TIME = int(JOIN_TIME)
MAX_GROUPS = int(MAX_GROUPS)

welcome_text = "------ WELCOME ------\n"
welcome_text += "Redis:         " + colors.OKGREEN + "is ok!" + colors.ENDC + "\n"
welcome_text += "JOIN_TIME:     " + colors.UNDERLINE + str(JOIN_TIME) + colors.ENDC + "\n" 
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
    msg = str(event.raw_text)
    params = msg.split(' ')
    me = await client.get_me()

    # Ping
    if msg == '!ping':
        await event.reply("**PONG!**")
    
    # Detecting links & save to join later
    if ('t.me' in msg or 'telegram.me' in msg) and '/joinchat' in msg and 'AAAAA' not in msg:
        regex = r"\b(t.me|telegram.me)\/(joinchat)\/[-A-Z0-9+&@#\/%?=~_|$!:,.;]*[A-Z0-9+&@#\/%=~_|$]"
        matches = re.finditer(regex, msg, re.IGNORECASE)

        for matchNum, match in enumerate(matches, start=1):
            link = match.group()

            # if not r.sismember( cnf("All_Links"), link):
            r.sadd( cnf("All_Links"), link)
            r.sadd( cnf("Links"), link)
            print(link + " saved!")

    # Stats
    elif msg == '!stats':
        message = await event.reply("**Loading stats...**")
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

        stats = "**My Stats**\n\nUsers: `{}`\nGroups: `{}`\nChannels: `{}`\nBots: `{}`\nAll: `{}`\n\n**RAM Usage: %{}**\n**CPU Usage: %{}**\n**Disk Usage: %{}**".format(count_users, count_groups, count_channels, count_bots, count_all, psutil.virtual_memory()[2], psutil.cpu_percent(), psutil.disk_usage('/')[3])
        await client.edit_message(message, stats)
    
    # Set configs
    elif '!set ' in msg and isinstance(params[1], str) and params[2]:
        config_name = params[1]
        config_value = params[2]

        if config_name == "cron" and config_value.isdigit():
            CRON_TIME = int(config_value)
            r.set( cnf('CRON_TIME'), CRON_TIME)
            done = "Bot cron time has been set to {0}".format(config_value)

        elif config_name == "groups" and config_value.isdigit():
            MAX_GROUPS = int(config_value)
            r.set( cnf('MAX_GROUPS'), MAX_GROUPS)
            done = "Bot max groups has been set to {0}".format(config_value)

        elif config_name == "join" and config_value.isdigit():
            JOIN_TIME = int(config_value)
            r.set( cnf('JOIN_TIME'), JOIN_TIME)
            done = "Bot join time has been set to {0}".format(config_value)

        elif config_name == "bot":
            BOT_USER = str(config_value)
            r.set( cnf('BOT_USER'), BOT_USER)
            done = "Bot adverstiment user has been set to {0}".format(config_value)
        
        if done:
            print(done)
            await event.reply(done)
        else:
            await event.reply("Wrong key or value entered!")
    else:
        if isinstance(event.to_id, types.PeerUser):
            await event.reply("Adverstiment here!")

# Create cron event
def create_cron_event():    
    loop = asyncio.get_event_loop()
    task = loop.create_task( join_groups_task() )
    task = loop.create_task( adverstiment_task() )
    loop.run_until_complete(task)

# Join a group every JOIN_TIME seconds
async def join_groups_task():
    while True:
        link = r.spop( cnf("Links") )
        if link == None:
            break

        link = link.decode()
        link = link.replace('\n', '')
        link_hash = link.rsplit('/', 1)[-1]

        import_chat = await client(functions.messages.ImportChatInviteRequest(
            hash=link_hash
        ))
        group_id = import_chat.chats[0].id
        r.sadd( cnf("Chats"), group_id)
        print("A group added, chat_id: {0}".format(str(group_id)))
        await asyncio.sleep(JOIN_TIME)

# Send Adverstiment every CRON_TIME seconds
async def adverstiment_task():
    while True:
        await asyncio.sleep(CRON_TIME)

try:
    client.start()
    task = create_cron_event()
    client.run_until_disconnected()
except Exception as error:
    client_has_error(error)