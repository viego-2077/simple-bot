import discord
from discord.ext import commands

class AvatarBanner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_target_user(self, ctx, user: discord.User | None):
        """Lấy user từ mention, reply hoặc chính mình"""
        if user:
            return user
        if ctx.message.reference:
            ref_msg = ctx.message.reference.resolved
            if isinstance(ref_msg, discord.Message):
                return ref_msg.author
        return ctx.author

    @commands.command(name="av", aliases=["avatar"])
    async def avatar(self, ctx, *, user: discord.User = None):
        """Hiển thị avatar"""
        user = await self.get_target_user(ctx, user)

        embed = discord.Embed(
            title=f"🌐{user} Avatar",
            color=discord.Color.blue()
        )

        # Global avatar (ảnh lớn)
        if user.avatar:
            embed.description = f"[Link]({user.avatar.url})"
            embed.set_image(url=user.avatar.url)
        else:
            embed.description = "❌không có avatar."

        # Nếu là thành viên server và có avatar server khác global
        if isinstance(ctx.author, discord.Member):
            member = ctx.guild.get_member(user.id)
            if member and member.display_avatar and member.display_avatar.url != user.avatar.url:
                embed.add_field(
                    name="🖼 Avatar server",
                    value=f"[Link]({member.display_avatar.url})",
                    inline=False
                )

        await ctx.send(embed=embed)

    @commands.command(name="banner")
    async def banner(self, ctx, *, user: discord.User = None):
        """Hiển thị banner"""
        user = await self.get_target_user(ctx, user)
        user = await self.bot.fetch_user(user.id)  # fetch để lấy banner

        embed = discord.Embed(
            title=f"{user} Banner",
            color=discord.Color.purple()
        )

        if user.banner:
            embed.description = f"[Link ảnh]({user.banner.url})"
            embed.set_image(url=user.banner.url)
        else:
            embed.description = "❌không có banner."

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AvatarBanner(bot))
