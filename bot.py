import discord
import requests
import base64
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
    
    text = ""
    image_uri = None
    
    if message.content:
        text = message.content
    
    if message.attachments:
        attachment = message.attachments[0]
        img_bytes = await attachment.read()
        b64 = base64.b64encode(img_bytes).decode('utf-8')
        image_uri = f"data:image/png;base64,{b64}"
    
    print("Input: " + text)
    payload = {
        "prompt": text,
        "image": image_uri
    }
    
    response = requests.post(url, json=payload)
    output = response.json()["text"]

    if response.status_code==200:
        await message.channel.send(output)
    else:
        await message.channel.send("すみません．通信が悪いみたいです...")
        
client.run(DISCORD_TOKEN)
