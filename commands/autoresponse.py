# commands/autoresponse.py

import discord

from discord.ext import commands

import json

import os

import asyncio

import re

import string

DATA_FILE = "autoresponses.json"

DEFAULT_TIMEOUT = 20.0  # timeout cho từng bước nhập

# Các ký tự dấu câu/bìa thường gặp để strip ở đầu/cuối

EXTRA_PUNCT = ''.join([

    '"', "'", "“", "”", "‘", "’", "…", "—", "–", "«", "»", "•", "·"

])

STRIP_CHARS = string.punctuation + EXTRA_PUNCT + " \t\n\r"

class AutoResponse(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.responses = self.load_responses()

    def load_responses(self):

        """Load và migrate nếu file còn định dạng cũ."""

        if os.path.exists(DATA_FILE):

            with open(DATA_FILE, "r", encoding="utf-8") as f:

                try:

                    data = json.load(f)

                except json.JSONDecodeError:

                    return {}

            # Migrate: nếu value là string -> chuyển thành dict {"response":..., "mode":1}

            changed = False

            for guild_id, mapping in list(data.items()):

                if isinstance(mapping, dict):

                    for trig, val in list(mapping.items()):

                        if isinstance(val, str):

                            data[guild_id][trig] = {"response": val, "mode": 1}

                            changed = True

                        elif isinstance(val, dict):

                            # ensure keys

                            if "response" not in val:

                                val["response"] = ""

                                changed = True

                            if "mode" not in val:

                                val["mode"] = 1

                                changed = True

                else:

                    data[guild_id] = {}

                    changed = True

            if changed:

                with open(DATA_FILE, "w", encoding="utf-8") as f:

                    json.dump(data, f, ensure_ascii=False, indent=2)

            return data

        return {}

    def save_responses(self):

        with open(DATA_FILE, "w", encoding="utf-8") as f:

            json.dump(self.responses, f, ensure_ascii=False, indent=2)

    # ===== ARADD =====

    @commands.command(name="aradd")

    @commands.has_permissions(manage_messages=True)

    async def aradd(self, ctx):

        """Thêm auto response."""

        await ctx.send("**Nhập trigger:")

        def check(m):

            return m.author == ctx.author and m.channel == ctx.channel

        try:

            trig_msg = await self.bot.wait_for("message", timeout=DEFAULT_TIMEOUT, check=check)

        except asyncio.TimeoutError:

            return await ctx.send("⌛ Hết thời gian nhập.")

        trigger = trig_msg.content.strip()

        if not trigger:

            return await ctx.send("❌ Trigger trống.")

        if len(trigger) > 100:

            return await ctx.send("❌ Trigger quá dài.")

        await ctx.send("**nhập response:**")

        try:

            resp_msg = await self.bot.wait_for("message", timeout=DEFAULT_TIMEOUT, check=check)

        except asyncio.TimeoutError:

            return await ctx.send("⌛ Hết thời gian.")

        response = resp_msg.content.strip()

        if not response:

            return await ctx.send("❌ Response trống")

        await ctx.send("🛠 **Chọn mode:1/2**"

        )

        try:

            mode_msg = await self.bot.wait_for("message", timeout=DEFAULT_TIMEOUT, check=check)

        except asyncio.TimeoutError:

            return await ctx.send("⌛ Hết thời gian.")

        mode_choice = mode_msg.content.strip()

        if mode_choice not in ("1", "2"):

            return await ctx.send("❌ Lựa chọn không hợp lệ — hủy. Vui lòng nhập `1` hoặc `2`.")

        mode = int(mode_choice)

        guild_id = str(ctx.guild.id)

        if guild_id not in self.responses:

            self.responses[guild_id] = {}

        # Lưu trigger theo nguyên dạng người dùng nhập (key)

        self.responses[guild_id][trigger] = {"response": response, "mode": mode}

        self.save_responses()

        mode_text = "Luôn rep (substring)" if mode == 1 else "Exact full message (cả câu phải đúng trigger)"

        await ctx.send(f"Đã thêm auto response.")

    # ===== ARLIST =====

    @commands.command(name="arlist")

    async def arlist(self, ctx):

        """Hiển thị danh sách auto response của server."""

        guild_id = str(ctx.guild.id)

        if guild_id not in self.responses or not self.responses[guild_id]:

            return await ctx.send("📭 Server này chưa có auto response nào.")

        desc_lines = []

        for i, (trig, info) in enumerate(self.responses[guild_id].items(), start=1):

            mode = info.get("mode", 1)

            mode_text = "Mode1 (substring)" if mode == 1 else "Mode2 (exact full message)"

            resp = info.get("response", "")

            desc_lines.append(f"**{i}.** `{trig}` → {resp} — *{mode_text}*")

        desc = "\n".join(desc_lines)

        if len(desc) > 4000:

            desc = desc[:3990] + "\n... (vẫn còn)"

        embed = discord.Embed(title="Danh sách Auto Response", description=desc, color=discord.Color.green())

        await ctx.send(embed=embed)

    # ===== ARREMOVE =====

    @commands.command(name="arremove")

    @commands.has_permissions(manage_messages=True)

    async def arremove(self, ctx, *, trigger: str = None):

        """

        Xóa auto response

        """

        guild_id = str(ctx.guild.id)

        if guild_id not in self.responses or not self.responses[guild_id]:

            return await ctx.send("❌ Server này chưa có auto response nào để xóa.")

        if not trigger:

            return await ctx.send("⚠️ Dùng: `!arremove <tên trigger hoặc số thứ tự>`")

        data = self.responses[guild_id]

        removed_key = None

        # Nếu nhập số thứ tự

        if trigger.isdigit():

            idx = int(trigger)

            keys = list(data.keys())

            if 1 <= idx <= len(keys):

                removed_key = keys[idx - 1]

        else:

            # tìm exact trước

            lowered = trigger.lower()

            for key in data.keys():

                if key.lower() == lowered:

                    removed_key = key

                    break

            # nếu không exact, tìm chứa (gần đúng)

            if not removed_key:

                for key in data.keys():

                    if lowered in key.lower():

                        removed_key = key

                        break

        if not removed_key:

            return await ctx.send("❌ Không tìm thấy trigger phù hợp để xóa.")

        del data[removed_key]

        self.save_responses()

        await ctx.send(f"🗑️ Đã xóa auto response `{removed_key}`")

    # ===== MESSAGE LISTENER =====

    @commands.Cog.listener()

    async def on_message(self, message: discord.Message):

        # Bỏ qua bot hoặc DM

        if message.author.bot or not message.guild:

            return

        guild_id = str(message.guild.id)

        if guild_id not in self.responses:

            return

        content = message.content

        if not content:

            return

        # duyệt triggers theo thứ tự lưu — dừng ở trigger đầu tiên khớp

        for trig, info in self.responses[guild_id].items():

            mode = int(info.get("mode", 1))

            response = info.get("response", "")

            if mode == 1:

                # substring match (không phân biệt hoa thường)

                if trig.lower() in content.lower():

                    try:

                        await message.channel.send(response)

                    except Exception:

                        pass

                    break

            else:

                # mode 2: exact full message match (sau strip đầu/cuối dấu câu & whitespace)

                # Lấy nội dung và strip whitespace/dấu câu ở hai đầu

                normalized = content.strip().strip(STRIP_CHARS)

                if normalized.lower() == trig.lower():

                    try:

                        await message.channel.send(response)

                    except Exception:

                        pass

                    break

async def setup(bot):

    await bot.add_cog(AutoResponse(bot))