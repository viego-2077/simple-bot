import discord
from discord.ext import commands
import json
import os
import asyncio

DATA_FILE = "welcome_config.json"

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()

    # ==================== LOAD / SAVE ====================
    def load_config(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    # ==================== SETWLC ====================
    @commands.command(name="setwlc")
    @commands.has_permissions(manage_guild=True)
    async def setwlc(self, ctx, channel: discord.TextChannel = None):
        """set welcom chanel."""
        if channel is None:
            channel = ctx.channel

        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}

        self.config[guild_id]["channel_id"] = channel.id
        self.save_config()

        await ctx.send(f"welcom chanel: {channel.mention}")

    # ==================== SETTEXT ====================
    @commands.command(name="settext")
    @commands.has_permissions(manage_guild=True)
    async def settext(self, ctx):
        """set welcom text."""
        await ctx.send(
            "📝 **Nhập nội dung tin nhắn chào mừng:**"
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("⌛ Hết thời gian nhập.")

        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}

        self.config[guild_id]["welcome_text"] = msg.content
        self.save_config()

        await ctx.send("✅ Đã lưu nội dung tin nhắn chào mừng.")

    # ==================== MEMBER JOIN LISTENER ====================
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        if guild_id not in self.config:
            return

        settings = self.config[guild_id]
        channel_id = settings.get("channel_id")
        message_template = settings.get("welcome_text")

        if not channel_id or not message_template:
            return

        channel = member.guild.get_channel(channel_id)
        if not channel:
            return

        # Thay thế placeholder
        message = message_template.replace("-memberjoin-", member.mention)
        await channel.send(message)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
