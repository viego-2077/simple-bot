# creator: 2077 

import discord

from discord.ext import commands

import json

import os

import aiohttp


with open("config.json", "r", encoding="utf-8") as f:

    config = json.load(f)

intents = discord.Intents.default()

intents.message_content = True

intents.members = True


prefix = config.get("prefix", "!")

if prefix.isalpha():

    prefixes = [prefix, prefix.upper()]

else:

    prefixes = [prefix]

print(f"Prefix hiện tại: {prefixes}")



bot = commands.Bot(

    command_prefix=prefixes,

    case_insensitive=True,

    intents=intents

)


async def load_commands():

    for filename in os.listdir("./commands"):

        if filename.endswith(".py"):

            await bot.load_extension(f"commands.{filename[:-3]}")

            print(f"Đã tải {filename}")



@bot.event

async def on_ready():



    if not hasattr(bot, "session") or bot.session.closed:

        bot.session = aiohttp.ClientSession()

    print(f"Bot Login: {bot.user}!")

    await load_commands()

    print("Đã tải tất cả command.")



@bot.event

async def on_close():

    if hasattr(bot, "session") and not bot.session.closed:

        await bot.session.close()



bot.run(config["token"])
