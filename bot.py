import discord
import requests
from config import DISCORD_TOKEN

url = "http://localhost:8000/generate"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("ready...")
    
@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    text = message.content
    image = None
    
    if message.attachments:
        image = message.attachments[0].url
    
    print("Input: "+text)
    payload = {
        "prompt": text,
        "image": image
    }
    
    response = requests.post(url, json=payload)
    output = response.json()["text"]

    if response.status_code==200:
        await message.channel.send(output)
    else:
        await message.channel.send("すみません．通信が悪いみたいです...")
        
client.run(DISCORD_TOKEN)
