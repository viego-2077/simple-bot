# commands/nuke.py
import discord
from discord.ext import commands
import asyncio

class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nuke")
    @commands.guild_only()
    async def nuke(self, ctx):
        """
        nuke chanel
        """
        # Kiểm tra quyền người dùng
        if not ctx.author.guild_permissions.manage_channels:
            await ctx.send("❌ Bạn cần quyền `Manage Channels` để dùng lệnh này.")
            return

        # Kiểm tra quyền bot
        me = ctx.guild.me
        if not ctx.me.guild_permissions.manage_channels:
            await ctx.send("❌ Bot cần quyền `Manage Channels` để thực hiện thao tác này.")
            return

        channel = ctx.channel

        # Chỉ hỗ trợ TextChannel (nhưng nếu là VoiceChannel, có thể mở rộng sau)
        if not isinstance(channel, discord.abc.GuildChannel):
            await ctx.send("❌ Không thể thực hiện.")
            return

        # Gửi cảnh báo và chờ xác nhận (gõ "NUKE" trong 20s)
        warning = await ctx.send(
            f"⚠️ **hãy gõ `NUKE` để xác nhận.**"
        )

        def check(m: discord.Message):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.strip().lower() == "nuke"

        try:
            await ctx.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await warning.edit(content="⌛ Hết thời gian xác nhận.")
            return

        # Lưu thuộc tính cần thiết trước khi clone
        overwrites = channel.overwrites
        category = channel.category
        name = channel.name
        topic = getattr(channel, "topic", None)
        nsfw = getattr(channel, "nsfw", False)
        slowmode_delay = getattr(channel, "slowmode_delay", None)
        position = channel.position
        bitrate = getattr(channel, "bitrate", None)  # nếu voice chanel
        user_limit = getattr(channel, "user_limit", None)

        try:
            # Clone channel (giữ tên)
            # clone() tự copy permission overwrites và category
            new_channel = await channel.clone(name=name, reason=f"Nuked by {ctx.author}",)
            # Sửa một số thuộc tính không được clone mặc định (nếu cần)
            # topic, nsfw, slowmode_delay, etc.
            kwargs = {}
            if topic is not None:
                kwargs["topic"] = topic
            if nsfw is not None:
                kwargs["nsfw"] = nsfw
            if slowmode_delay is not None:
                kwargs["slowmode_delay"] = slowmode_delay
            if bitrate is not None:
                kwargs["bitrate"] = bitrate
            if user_limit is not None:
                kwargs["user_limit"] = user_limit

            if kwargs:
                try:
                    await new_channel.edit(**kwargs, reason=f"Restore attributes after nuke by {ctx.author}")
                except Exception:
                    # không block nếu một số thuộc tính không thể set (ví dụ text vs voice)
                    pass

            # Di chuyển vị trí kênh mới về vị trí kênh cũ
            try:
                await new_channel.edit(position=position)
            except Exception:
                # Một số server/role layouts có thể không cho đổi position, bỏ qua nếu lỗi
                pass

            # Xóa kênh cũ
            await channel.delete(reason=f"Nuked by {ctx.author}")

            # Gửi thông báo trong kênh mới (nếu bot có quyền send_messages)
            try:
                await new_channel.send(f"💥 nuked by {ctx.author.mention}.")
            except Exception:
                # không cần làm gì nếu không thể gửi tin
                pass

        except Exception as e:
            await ctx.send(f"❌ error: `{e}`")

async def setup(bot):
    await bot.add_cog(Nuke(bot))
