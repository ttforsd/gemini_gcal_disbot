from dotenv import load_dotenv
import discord
import os
from llm import LLM
import asyncio
from gcal import write2gcal, del_event
from database import database



model = LLM()




load_dotenv(override=True)



user_map = {
    os.getenv("DISCORD_NAME_0"): os.getenv("NAME_0"),
    os.getenv("DISCORD_NAME_1"): os.getenv("NAME_1")
}


tz_map = {
    os.getenv("DISCORD_NAME_0"): os.getenv("TZ_0"),
    os.getenv("DISCORD_NAME_1"): os.getenv("TZ_1")
}


token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
special_command = os.getenv("COMMAND_1")

async def llm_wrapper(prompt, time_zone="Europe/London"):
    # get loop 
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, model.main, prompt, time_zone)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    switch = False 
    print(message.content)

    del_command = "!del"
    if message.content[:len(del_command)] == del_command:
        entry_id = message.content[len(del_command):]
        entry_id = entry_id.strip()
        try: 
            entry_id = int(entry_id)
        except: 
            await message.channel.send(f"Invalid entry ID: {entry_id}, only integers are allowed")
            return
        
        db = database()
        event_ids = db.get_events_by_entry_id(entry_id)
        if not event_ids:
            await message.channel.send(f"Entry ID: {entry_id} not found")
            return
        for event_id in event_ids:
            gres = del_event(event_id)
            await message.channel.send(gres)
        dres = db.delete_entry_by_id(entry_id)
        if dres: 
            await message.channel.send(f"Entry ID: {entry_id} deleted")
        else: 
            await message.channel.send(f"An error occurred while deleting entry ID: {entry_id} from the database")
        return 

        

    if len(special_command) <= len(message.content) and special_command == message.content[:len(special_command)]:
        switch = True
        message_content = message.content[len(special_command):]
    else: 
        message_content = message.content
    await message.channel.send(f"Processing '{message_content}' to make calendar event")

    if switch: 
        user = os.getenv("NAME_1")
        tz = os.getenv("TZ_1")
    else: 
        user = user_map[message.author.global_name]
        tz = tz_map[message.author.global_name]
    
    # Call the LLM model to generate the event in background
    if not message.attachments: 
        response = await model.main(message_content, time_zone=tz)
    else: 
        for attachment in message.attachments: 
            url = attachment.url
            response = await model.vision_main(url, tz)
    if type(response) != list: 
        response = [response]


    # Call the Google Calendar API to write the event
    try:
        event_ids = [] 
        for event in response:
            event["summary"] = f"{user}: {event['summary']}"
            summary, dt, link, event_id = write2gcal(event)
            msg = f"Event: {summary} on {dt}. Link: {link}"
            event_ids.append(event_id)
            await message.channel.send(msg)
        db = database()
        entry_id = db.events_entry(event_ids)
        await message.channel.send(f"Entry ID: {entry_id}")

    except Exception as e:
        await message.channel.send(f"An error occurred: {e}")




bot.run(token)
