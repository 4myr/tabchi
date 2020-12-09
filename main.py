from telethon import TelegramClient, events

from telethon.sync import TelegramClient
from telethon import functions, types, errors

import config
import redis
import sys, os, asyncio

# Handle multiple instances without any duplicate
# instance = input('Enter your instance name [example: amyr]: ') if len(sys.argv) < 2 else sys.argv[1]
instance = "amyr"
instance_path = os.path.abspath("Sessions/{0}".format(instance))

# A simply function for showing errors
def client_has_error(error):
    print("[Error]: ", error)

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

# Create timer event to handling tasks need timer
def create_timer_event():    
    loop = asyncio.get_event_loop()
    timer_task = timer(2)
    task = loop.create_task(timer_task)
    loop.run_until_complete(task)

# All codes need timer write here
async def timer(time):
    while True:
        print("Task working!")
        await asyncio.sleep(time)

try:
    client.start()
    task = create_timer_event()
    client.run_until_disconnected()
except Exception as error:
    client_has_error(error)