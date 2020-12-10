from telethon import TelegramClient, events

from telethon.sync import TelegramClient
from telethon import functions, types, errors

import config
import redis
import sys, os, asyncio, psutil, re, logging

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
CRON_TIME = r.get( cnf("CRON_TIME") ) or 120
JOIN_TIME = r.get( cnf("JOIN_TIME") ) or 200
MAX_GROUPS = r.get( cnf("MAX_GROUPS") ) or 150
BOT_USER = r.get( cnf("BOT_USER") ) or None # configured BOT_USER will replace on adverstiment texts for {BOT_USER}

CRON_TIME = int(CRON_TIME)
JOIN_TIME = int(JOIN_TIME)
MAX_GROUPS = int(MAX_GROUPS)

r.set( cnf("CRON_TIME"), CRON_TIME )
r.set( cnf("JOIN_TIME"), JOIN_TIME )
r.set( cnf("MAX_GROUPS"), MAX_GROUPS )


BLOCKED_GROUPS = {
    'تبلیغ',
    'کسب و کار',
    'نیاز',
    'آگهی',
    'اگهی',
    'بازار',
    'دیوار',
    'سراسری',
    'شیپور'
}

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

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING)

# An event to handle new messages
@client.on(events.NewMessage)
async def newMessage(event):
    global MAX_GROUPS, CRON_TIME, JOIN_TIME, BOT_USER
    msg = str(event.raw_text)
    params = msg.split(' ')
    me = await client.get_me()

    sender = await event.get_sender()
    chat_id = event.chat_id
    sender_id = event.sender_id

    # Ping
    if msg == '!ping':
        await event.reply("**PONG!**")
    
    # Detecting links & save to join later
    if ('t.me' in msg or 'telegram.me' in msg) and '/joinchat' in msg and 'AAAAA' not in msg:
        regex = r"\b(t.me|telegram.me)\/(joinchat)\/[-A-Z0-9+&@#\/%?=~_|$!:,.;]*[A-Z0-9+&@#\/%=~_|$]"
        matches = re.finditer(regex, msg, re.IGNORECASE)

        for matchNum, match in enumerate(matches, start=1):
            link = match.group()

            if not r.sismember("All_Links", link):
                r.sadd("All_Links", link)
                r.sadd("Links", link)
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

        random_adverstiments = r.scard("Adverstiments")
        random_banners = r.scard("Banners")
        saved_links = r.scard("All_Links")
        saved_groups = r.scard( cnf("Chats") )
        saved_users = r.scard( cnf("Users") )
        stats = "**My Stats**\n\nUsers: `{}`\nGroups: `{}`\nSaved Groups: `{}`\nChannels: `{}`\nBots: `{}`\nAll: `{}`\n\n**RAM Usage: %{}**\n**CPU Usage: %{}**\n**Disk Usage: %{}**\n\n".format(count_users, count_groups, saved_groups, count_channels, count_bots, count_all, psutil.virtual_memory()[2], psutil.cpu_percent(), psutil.disk_usage('/')[3])
        stats += "**Configs:**\n\nMax Groups: `{}`\nJoin Delay: `{}`\nAdverstiment Delay: `{}`\nBot User: {}\nRandom Adverstiments: `{}`\nRandom Banners: `{}`\nSaved Links: `{}`\nUsers Received Adverstiment: `{}`".format(MAX_GROUPS, JOIN_TIME, CRON_TIME, BOT_USER, random_adverstiments, random_banners, saved_links, saved_users)
        await client.edit_message(message, stats)
    
    # Set configs
    elif '!set ' in msg and isinstance(params[1], str) and params[2]:
        config_name = params[1]
        config_value = params[2]

        # Adverstiment timer value
        if config_name == "cron" and config_value.isdigit():
            CRON_TIME = int(config_value)
            r.set( cnf('CRON_TIME'), CRON_TIME)
            done = "Bot cron time has been set to {0}".format(config_value)

        # Max groups that bot can join
        elif config_name == "groups" and config_value.isdigit():
            MAX_GROUPS = int(config_value)
            r.set( cnf('MAX_GROUPS'), MAX_GROUPS)
            done = "Bot max groups has been set to {0}".format(config_value)

        # Joining groups timer value
        elif config_name == "join" and config_value.isdigit():
            JOIN_TIME = int(config_value)
            r.set( cnf('JOIN_TIME'), JOIN_TIME)
            done = "Bot join time has been set to {0}".format(config_value)

        # This config will replaced on adverstiment text for {BOT_USER}
        elif config_name == "bot":
            BOT_USER = str(config_value)
            r.set( cnf('BOT_USER'), BOT_USER)
            done = "Bot adverstiment user has been set to {0}".format(config_value)
        
        if done:
            print(done)
            await event.reply(done)
        else:
            await event.reply("Wrong key or value entered!")

    # Clear Database
    elif '!clear ' in msg:
        config = msg.split(' ')[1]
        done = "Wrong key or value entered!"
        if config == 'adv':
            r.delete("Adverstiments")
            done = "Adverstiments has been cleared!"
        elif config == 'users':
            r.delete(cnf("Users"))
            done = "Users received adverstiment has been cleared!"
        print(done)
        await event.reply(done)

    # Adverstiments management (this adverstiments will send randomly to groups every CRON_TIME)
    elif '!adv' in msg:
        args = msg.split(' ', 1)
        
        # Get all adverstiment texts list
        if len(args) == 1:
            advs = r.smembers("Adverstiments")
            advs = list(advs)
            texts = ""
            for x in advs:
                texts += "\n▫️ {0}".format(x.decode())
            await event.reply("Your adverstiments texts:\n{0}".format(texts))
        
        # Add new adverstiment text
        else:
            adverstiment_text = args[1]
            r.sadd("Adverstiments", adverstiment_text)
            done = "New adverstiment text added:\n\n{0}".format(adverstiment_text)
            print(done)
            await event.reply(done)

    # Banners management (this banners will send randomly to user on sending private message)
    elif '!banner' in msg:
        args = msg.split(' ', 1)
        
        # Get all banners list
        if len(args) == 1:
            banners = r.smembers("Banners")
            banners = list(banners)
            texts = ""
            for x in banners:
                texts += "\n▫️ {0}".format(x.decode())
            await event.reply("Your banners texts:\n{0}".format(texts))
        
        # Add new banner text
        else:
            banner_text = args[1]
            r.sadd("Banners", banner_text)
            done = "New banner text added:\n\n{0}".format(banner_text)
            print(done)
            await event.reply(done)

    else:
        # if a user sent a message in private, sending specific adverstiment
        if isinstance(event.to_id, types.PeerUser):
            random_banner = r.srandmember("Banners").decode()
            if random_banner == None:
                print("No banner!")
            elif r.sismember( cnf("Users"), sender_id):
                # Replace {bot}
                if BOT_USER:
                    random_banner.replace('{bot}', BOT_USER)
                await event.reply(random_banner)
                r.sadd( cnf("Users"), sender_id)

# Create cron event
def create_cron_events():    
    loop = asyncio.get_event_loop()
    task = loop.create_task( join_groups_task() )
    task = loop.create_task( adverstiment_task() )
    loop.run_until_complete(task)

# Join a group every JOIN_TIME seconds
async def join_groups_task():
    while True:
        try:
            if r.scard( cnf('Chats') ) < MAX_GROUPS:
                # Pop a link to join that
                link = r.spop("Links")
                if link == None:
                    print("No link!")
                else:
                    link = link.decode()
                    link = link.replace('\n', '')
                    link_hash = link.rsplit('/', 1)[-1]

                    # Joining to group
                    import_chat = await client(functions.messages.ImportChatInviteRequest(
                        hash=link_hash
                    ))

                    group_id = import_chat.chats[0].id
                    group_title = import_chat.chats[0].title

                    # Check if group title contains blocked titles
                    is_blocked = False
                    for b in BLOCKED_GROUPS:
                        if b in group_title:
                            is_blocked = True
                    
                    if not is_blocked:
                        r.sadd( cnf("Chats"), group_id)
                        print("A group ({0}) added, chat_id: {1}".format(group_title, str(group_id)))
                    else:
                        await client.delete_dialog(group_id)
                        print("A group ({0}) has detected as blocked & deleted.".format(group_title))
            else:
                print("Join action fails because of max groups.")
        except Exception as error
            client_has_error("Error in join_groups_task: " + error)
        await asyncio.sleep(JOIN_TIME)

# Send Adverstiment every CRON_TIME seconds
async def adverstiment_task():
    while True:
        try:
            random_chat_id = r.srandmember( cnf("Chats") )
            random_adverstiment = r.srandmember("Adverstiments")
            if random_chat_id == None:
                print("No chats!")
            elif random_adverstiment == None:
                print("No adverstiment!")
            else:
                random_chat_id = int(random_chat_id)
                random_adverstiment = random_adverstiment.decode()
                await client.send_message(random_chat_id, random_adverstiment)
        except Exception as error
            client_has_error("Error in adverstiment_task: " + error)
        await asyncio.sleep(CRON_TIME)

try:
    client.start()
    task = create_cron_events()
    client.run_until_disconnected()
except asyncio.CancelledError:
    raise
except Exception as error:
    print(error)
    client_has_error(error)