import discord
from discord.ext import commands
import json
import os
from datetime import datetime

DATA_FILE = "snipe.json"
MAX_SNIPES = 20  # Lưu tối đa 20 tin nhắn bị xóa

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipes = self.load_snipes()

    # ==========================
    # Load / Save dữ liệu
    # ==========================
    def load_snipes(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_snipes(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.snipes, f, ensure_ascii=False, indent=2)

    # ==========================
    # Khi có tin nhắn bị xóa
    # ==========================
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.content or message.author.bot:
            return

        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)

        if guild_id not in self.snipes:
            self.snipes[guild_id] = {}
        if channel_id not in self.snipes[guild_id]:
            self.snipes[guild_id][channel_id] = []

        # Thêm tin nhắn vào danh sách
        self.snipes[guild_id][channel_id].insert(0, {
            "author": str(message.author),
            "author_id": message.author.id,
            "content": message.content,
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Giới hạn tối đa 20 tin / kênh
        if len(self.snipes[guild_id][channel_id]) > MAX_SNIPES:
            self.snipes[guild_id][channel_id] = self.snipes[guild_id][channel_id][:MAX_SNIPES]

        self.save_snipes()

    # ==========================
    # Lệnh snipe — xem 1 tin gần nhất
    # ==========================
    @commands.command(name="snipe")
    async def snipe(self, ctx, *, option=None):
        guild_id = str(ctx.guild.id)
        channel_id = str(ctx.channel.id)

        if guild_id not in self.snipes or channel_id not in self.snipes[guild_id]:
            return await ctx.send("no snipe data.")

        snipes = self.snipes[guild_id][channel_id]

        # Nếu người dùng gõ "!snipe all"
        if option and option.lower() == "all":
            embed = discord.Embed(
                title=f"🕵️‍ message delete list",
                color=discord.Color.orange()
            )
            text = ""
            for i, s in enumerate(snipes[:MAX_SNIPES], start=1):
                text += f"**{i}.** **{s['author']}**: {s['content']}\n"
            embed.description = text[:4000]  # tránh vượt giới hạn embed
            return await ctx.send(embed=embed)

        # Nếu chỉ xem 1 tin gần nhất
        s = snipes[0]
        embed = discord.Embed(
            description=s["content"],
            color=discord.Color.orange(),
            timestamp=datetime.strptime(s["time"], "%Y-%m-%d %H:%M:%S")
        )
        embed.set_author(name=f"Người gửi: {s['author']}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Snipe(bot))
