import discord

from discord.ext import commands

import json

import os

import aiohttp

# ===== Đọc config =====

with open("config.json", "r", encoding="utf-8") as f:

    config = json.load(f)

intents = discord.Intents.default()

intents.message_content = True

intents.members = True

# ===== Xử lý prefix =====

prefix = config.get("prefix", "!")

if prefix.isalpha():

    prefixes = [prefix, prefix.upper()]

else:

    prefixes = [prefix]

print(f"📦 Prefix hiện tại: {prefixes}")

# ===== Khởi tạo bot =====

bot = commands.Bot(

    command_prefix=prefixes,

    case_insensitive=True,

    intents=intents

)

# ===== Tải các lệnh trong thư mục commands =====

async def load_commands():

    for filename in os.listdir("./commands"):

        if filename.endswith(".py"):

            await bot.load_extension(f"commands.{filename[:-3]}")

            print(f"✅ Đã tải {filename}")

# ===== Khi bot online =====

@bot.event

async def on_ready():

    # ⚙️ Tạo aiohttp session tại đây (đúng thời điểm có event loop)

    if not hasattr(bot, "session") or bot.session.closed:

        bot.session = aiohttp.ClientSession()

    print(f"✅ Bot đã đăng nhập thành công dưới tên {bot.user}!")

    await load_commands()

    print("📦 Đã tải tất cả command modules.")

# ===== Khi bot tắt =====

@bot.event

async def on_close():

    if hasattr(bot, "session") and not bot.session.closed:

        await bot.session.close()

# ===== Chạy bot =====

bot.run(config["token"])