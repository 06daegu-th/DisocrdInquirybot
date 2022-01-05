from os import system
from imp import reload
system('cls')
import discord 
import asyncio 
from source import add_message
from source import config

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    system('cls')
    print("봇이 준비 되었습니다")

@client.event
async def on_message(message):
    if message.author.bot:
        return None 
    if message.content.startswith("##리로드"):
        if message.author.id == 0 or message.author.id == 0 or message.author.id == 0:
            reload(add_message)
            reload(config)
            await message.reply(embed=discord.Embed(title="Module Reload", description="✅ 모든 모듈을 모두 다시 시작했습니다"))
    elif message.content.startswith("##정리"):
        system('cls')
    else:
        await add_message.go_message(client, message)
    

client.run("OTIyNzA3MzgxNjg1NzMxMzU4.YcFYNg.bX2CyrA9fz9w_JwdZ4NemNSGWII")
