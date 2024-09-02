from dotenv import load_dotenv
import discord
import os
from llm import LLM
import asyncio
from gcal import write2gcal



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
    response = await model.main(message_content, time_zone=tz)


    # Call the Google Calendar API to write the event
    try:
        for event in response:
            event["summary"] = f"{user}: {event['summary']}"
            res = write2gcal(event)
            await message.channel.send(res)
    except Exception as e:
        await message.channel.send(f"An error occurred: {e}")




bot.run(token)
