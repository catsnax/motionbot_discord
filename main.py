from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response
import requests
from datetime import datetime, timedelta
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = Intents.default()
intents.message_content = True #NOQA
client = Client(intents = intents)


async def sendMessage(message, user_message):
    if not user_message:
        print('message empty')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]
    
    try:
        response = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


@client.event
async def on_ready():
    print(f'{client.user} is running') 


parameters = {}
users = []

@client.event
async def on_message(message):
    global parameters
    global users
    if message.author == client.user:
        return

    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)
    print(f'[{channel}] {username} : {user_message}')

    if message.content.startswith('!veto'):
        parts = message.content.split()
        command = parts[0]
        params = parts[1:]
        
        parameters[message.author.id] = params
        users.append(message.author)

        await message.channel.send("hello im here now")
        await message.delete()
        
        if len(parameters) == 2:
            await process_command(parameters, users, message.channel)

    if message.content.startswith('!motion'):
        await generate_motion(message.channel)
    
    if message.content.startswith('!time'):
        await time_speech(message.channel)


async def process_command(parameters, users, channel):
    # Assuming you have received parameters from two users
    print("hello")
    user1_params = parameters.get(users[0].id)
    user2_params = parameters.get(users[1].id)

    # Do something with the parameters
    await channel.send(f"User 1 parameters: {user1_params}")
    await channel.send(f"User 2 parameters: {user2_params}")

    # Clear the parameters and users list for the next command
    parameters.clear()
    users.clear()

async def generate_motion(channel):
    url = 'http://127.0.0.1:8000/motions/'

    data = {'motionTheme' :'Any', 'motionDifficulty' : 'Any', 'motionFormat' : 'British Parliamentary'}

    response = requests.put(url, json = data)

    motion = response.json()

    if(motion['infoSlide'] != ''):
       await channel.send("**Infoslide**: " + motion['infoSlide'])

    await channel.send("**Motion**: " + motion['motionName'])


async def time_speech(channel):
    countdown_duration = timedelta(minutes=7) 
    start_time = datetime.now()

    message = await channel.send("7 minute countdown started")

    while True:
        elapsed_time = datetime.now() - start_time
        remaining_time = countdown_duration - elapsed_time
        if remaining_time <= timedelta():
            print("Countdown finished!")
            break

        if remaining_time.seconds % 5 == 0:
            remaining_time_str = str(remaining_time).split(".")[0]
            await message.edit(content=f"Remaining time: {remaining_time_str}")

        await asyncio.sleep(1)



def main():
    client.run(token = TOKEN)

if __name__ == '__main__':
    main()