import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==================== LOCK CHANNEL ====================
    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """Khóa kênh"""
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is False:
            return await ctx.send("🔒 Kênh đang bị khóa.")
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"🔒 Đã khóa kênh {channel.mention}.")

    # ==================== UNLOCK CHANNEL ====================
    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """Mở khóa kênh"""
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is True or overwrite.send_messages is None:
            return await ctx.send("🔓 Kênh không bị khóa.")
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"🔓 Đã mở khóa kênh {channel.mention}.")

    # ==================== ROLE FINDER ====================
    def find_role(self, guild, name: str):
        """Tìm role theo tên."""
        name = name.lower()
        role = discord.utils.get(guild.roles, name=name)
        if role:
            return role
        for r in guild.roles:
            if name in r.name.lower():
                return r
        return None

    # ==================== ADD ROLE ====================
    @commands.command(name="role")
    @commands.has_permissions(manage_roles=True)
    async def add_role(self, ctx, member: discord.Member, *, role_name: str):
        """Thêm role cho thành viên"""
        role = self.find_role(ctx.guild, role_name)
        if not role:
            return await ctx.send(f"Không tìm thấy role **{role_name}**.")
        if role in member.roles:
            return await ctx.send(f"{member.mention} đã có role này.")
        try:
            await member.add_roles(role, reason=f"Role add by {ctx.author}")
            await ctx.send(f"Đã thêm role **{role.name}** cho {member.mention}.")
        except discord.Forbidden:
            await ctx.send("❌ Bot không đủ quyền để thêm role này.")
        except Exception as e:
            await ctx.send(f"❌ Lỗi: {e}")

    # ==================== REMOVE ROLE ====================
    @commands.command(name="-role")
    @commands.has_permissions(manage_roles=True)
    async def remove_role(self, ctx, member: discord.Member, *, role_name: str):
        """Gỡ role khỏi thành viên"""
        role = self.find_role(ctx.guild, role_name)
        if not role:
            return await ctx.send("❌ Không tìm thấy role.")
        if role not in member.roles:
            return await ctx.send(f"{member.mention} không có role này.")
        try:
            await member.remove_roles(role, reason=f"Role remove by {ctx.author}")
            await ctx.send(f"✅ Đã gỡ role.")
        except discord.Forbidden:
            await ctx.send("❌ Bot không đủ quyền để gỡ role này.")
        except Exception as e:
            await ctx.send(f"❌ Lỗi: {e}")

    # ==================== KICK (mention hoặc ID) ====================
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: str, *, reason: str = "Không có lý do"):
        """Kick thành viên."""
        try:
            member = None
            if ctx.message.mentions:
                member = ctx.message.mentions[0]
            else:
                member = await ctx.guild.fetch_member(int(user))

            if not member:
                return await ctx.send("❌ Không tìm thấy thành viên.")
            if member == ctx.author:
                return await ctx.send("❌ không thể tự kick chính mình.")
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                return await ctx.send("❌ Bạn không đủ trình để kick người dùng này.")

            await member.kick(reason=f"{reason} (kick bởi {ctx.author})")
            await ctx.send(f"👢 Đã kick **{member}** khỏi server.\n💬 Lý do: {reason}")
        except Exception as e:
            await ctx.send(f"⚠️ Lỗi khi kick: `{e}`")

    # ==================== BAN (mention hoặc ID) ====================
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: str, *, reason: str = "Không có lý do"):
        """Ban thành viên."""
        try:
            member = None
            if ctx.message.mentions:
                member = ctx.message.mentions[0]
            else:
                try:
                    member = await ctx.guild.fetch_member(int(user))
                except:
                    member = None

            if member:
                if member == ctx.author:
                    return await ctx.send("❌ không thể tự ban chính mình.")
                if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                    return await ctx.send("❌ Bạn không đủ trình để Ban người dùng này.")
                await member.ban(reason=f"{reason} (ban bởi {ctx.author})")
                await ctx.send(f"🔨 Đã ban **{member}** khỏi server.\n💬 Lý do: {reason}")
            else:
                # Nếu người đó không còn trong server, ban qua ID
                user_obj = await self.bot.fetch_user(int(user))
                await ctx.guild.ban(user_obj, reason=f"{reason} (ban bởi {ctx.author})")
                await ctx.send(f"🔨 Đã ban **{user_obj}** (dùng ID).\n💬 Lý do: {reason}")
        except Exception as e:
            await ctx.send(f"⚠️ Lỗi khi ban: `{e}`")

    # ==================== UNBAN ====================
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user: str):
        """Unban"""
        try:
            async for ban_entry in ctx.guild.bans():
                u = ban_entry.user

                # Nếu nhập ID
                if user.isdigit() and int(user) == u.id:
                    await ctx.guild.unban(u, reason=f"unban bởi {ctx.author}")
                    return await ctx.send(f"✅ Đã unban **{u}** (ID: {u.id})")

                # Nếu nhập tên hoặc tên#0000
                if user.lower() in (f"{u.name}#{u.discriminator}".lower(), u.name.lower()):
                    await ctx.guild.unban(u, reason=f"unban bởi {ctx.author}")
                    return await ctx.send(f"✅ Đã unban **{u}**.")

            await ctx.send("❌ error: user này không bị ban.")
        except Exception as e:
            await ctx.send(f"⚠️ error: `{e}`")
# ==================== CLEAR MESSAGES ====================

    @commands.command(name="clear", aliases=["purge"])

    @commands.has_permissions(manage_messages=True)

    async def clear(self, ctx, amount: int = None):

        """

        Xóa tin nhắn

        """

        if amount is None:

            return await ctx.send("⚠️ Dùng: `!clear <số lượng>`.")

        if amount < 1:

            return await ctx.send("Số lượng phải lớn hơn 0.")

        if amount > 1000:

            return await ctx.send("Max = 1000.")

        try:

            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 để xóa luôn lệnh

            count = len(deleted) - 1

            confirm = await ctx.send(f"🧹 Đã xóa **{count}** tin nhắn.")

            await confirm.delete(delay=5)  # tự xóa thông báo sau 5 giây

        except discord.Forbidden:

            await ctx.send("❌ Bot không đủ quyền.")

        except Exception as e:

            await ctx.send(f"⚠️ Lỗi: `{e}`")

# ==================== TROM EMOJI (STEAL EMOJI) ====================

    @commands.command(name="trom", aliases=["steal", "addemoji"])

    @commands.has_permissions(manage_emojis=True)

    async def trom(self, ctx, emoji: str = None, *, name: str = None):

        """

        Lấy emoji từ server khác

        """

        if not emoji:

            return await ctx.send("⚠️ Dùng: `!trom <emoji> <tên_mới>`")

        if not name:

            return await ctx.send("⚠️ thiếu tên emoji.")

        try:

            # Trích xuất ID và link emoji

            if emoji.startswith("<a:"):  # emoji động (GIF)

                emoji_id = int(emoji.split(":")[2].replace(">", ""))

                is_animated = True

            elif emoji.startswith("<:"):  # emoji tĩnh

                emoji_id = int(emoji.split(":")[2].replace(">", ""))

                is_animated = False

            else:

                return await ctx.send("❌ chỉ trộm được custom emoji.")

            # Tạo link tải emoji

            url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if is_animated else 'png'}"

            # Tải emoji về

            async with self.bot.session.get(url) as resp:

                if resp.status != 200:

                    return await ctx.send("❌ Không thể tải emoji.")

                emoji_bytes = await resp.read()

            # Tạo emoji mới trong server

            new_emoji = await ctx.guild.create_custom_emoji(name=name, image=emoji_bytes, reason=f"stolen by {ctx.author}")

            await ctx.send(f"Đã thêm emoji mới: <{'a' if is_animated else ''}:{new_emoji.name}:{new_emoji.id}>")

        except discord.Forbidden:

            await ctx.send("❌ Bot không đủ quyền để thêm emoji.")

        except Exception as e:

            await ctx.send(f"⚠️ Lỗi: `{e}`")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
