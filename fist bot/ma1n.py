import discord
from discord.ext import commands
import json
import os

# Đọc config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix=config["prefix"], intents=intents)

# Tải các lệnh trong thư mục commands/
@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập thành công dưới tên {bot.user}!")
    await load_commands()
    print("📦 Đã tải tất cả command modules.")

async def load_commands():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            await bot.load_extension(f"commands.{filename[:-3]}")

# Khởi động bot
bot.run(config["token"])
