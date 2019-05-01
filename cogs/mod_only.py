from discord.ext import commands
from discord.utils import get
import discord
from datetime import datetime

from bot import Shiro
from util import strfdelta
from anilist_api import find_anime_by_id

import asyncio


class ModsCog(commands.Cog):
    def __init__(self, bot: Shiro):
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx):
        if self.bot.is_mod(ctx.author):
            timedif = strfdelta(datetime.utcnow() - self.bot.start_time)
            await ctx.send(content=f"I have been up for **{timedif}**!")

    @commands.command()
    async def purge(self, ctx, amount):
        if self.bot.is_mod(ctx.author):
            amount = int(amount)
            purge_list = []

            async for i in ctx.channel.history(limit=amount):
                purge_list.append(i)

            amount_deleted = purge_list.__len__()
            cycles = (amount_deleted // 100) + 1
            for i in range(cycles):
                delete_from = i * 100
                delete_to = (i + 1) * 100
                await ctx.channel.delete_messages(purge_list[delete_from:delete_to])
            embed = self.bot.basic_embed(True, "**{}** messages have been deleted!".format(amount_deleted))
            message = await ctx.send(embed=embed)
            self.bot.send_log(
                "Msg Purge",
                f"{ctx.message.author}: Purged {amount_deleted} messages in {ctx.message.channel} - "
                f"See list of purged messages below:\n")
            self.bot.send_log("Msg Purge", "====================================================================")
            for message in purge_list:
                user_name = f"{message.author}".ljust(18, " ")
                print(f"[{message.created_at}] {user_name}: {message.content}")
            self.bot.send_log("Msg Purge", "====================================================================")
            await asyncio.sleep(10)
            await message.delete()

    @commands.command()
    async def echo(self, ctx, destination, *args):
        if self.bot.is_mod(ctx.author):
            message = ""
            for string in args:
                message += (string + " ")
            message = message.strip()
            dest_channel_id = destination.replace("<", "").replace(">", "").replace("#", "")
            try:
                dest_channel_id = int(dest_channel_id)
                dest_channel = get(ctx.guild.channels, id=int(dest_channel_id))
            except ValueError:
                dest_channel = get(ctx.guild.channels, name=dest_channel_id)
            if not dest_channel:
                dest_channel = get(ctx.guild.channels, name=destination)
            if isinstance(dest_channel, discord.TextChannel):
                self.bot.send_log("Mod Echo", "{} sent a message via echo to #{}".format(
                    ctx.message.author, dest_channel.name, message))
                await dest_channel.send(content=message)
                embed = self.bot.basic_embed(True, "Message **sent**!")
                await ctx.send(embed=embed)
            else:
                self.bot.send_log("Mod Echo", "{} tried to send a message to {} (Failed)".format(
                    ctx.message.author, dest_channel, message))
                embed = self.bot.basic_embed(False, "Channel **not found**!")
                await ctx.send(embed=embed)

    @commands.command()
    async def mute(self, ctx, user_id):
        if self.bot.is_mod(ctx.author):
            user_id = self.bot.mention_cleanup(user_id)
            muted_user = self.bot.senko_guild.get_member(int(user_id))
            if muted_user:
                self.bot.send_log("Mute", "{}: Mute pending user {}({}) found: Applying mute.".format(
                    ctx.message.author, user_id, muted_user))
                await muted_user.add_roles(self.bot.roles.muted)
                embed = self.bot.basic_embed(True, "User **Muted**!")
                await ctx.send(embed=embed)
            else:
                self.bot.send_log("Mute", "{}: Mute pending user {}({}) not found.".format(
                    ctx.message.author, user_id, muted_user))
                embed = self.bot.basic_embed(False, "User **not found**!")
                await ctx.send(embed=embed)

    @commands.command()
    async def unmute(self, ctx, user_id):
        if self.bot.is_mod(ctx.author):
            user_id = self.bot.mention_cleanup(user_id)
            try:
                unmuted_user = self.bot.senko_guild.get_member(int(user_id))
                ismuted = get(unmuted_user.roles, id=self.bot.roles.muted.id)
                if unmuted_user:
                    if ismuted:
                        self.bot.send_log("Unmute", "{}: Unmute pending user {}({}) found: Removing mute.".format(
                            ctx.author, user_id, unmuted_user))
                        await unmuted_user.remove_roles(self.bot.roles.muted)
                        embed = self.bot.basic_embed(True, "User **Unmuted**!")
                    else:
                        self.bot.send_log("Unmute", "{}: Unmute pending user {}({}) found: ERROR! "
                                                    "User is not muted.".format(
                                                        ctx.message.author, user_id, unmuted_user))
                        embed = self.bot.basic_embed(False, "User is **not muted**!")
                else:
                    self.bot.send_log("Unmute", "{}: Unmute pending user {}({}) not found.".format(
                        ctx.message.author, user_id, unmuted_user))
                    embed = self.bot.basic_embed(False, "User **not found**!")
            except AttributeError:
                self.bot.send_log("Unmute", "{}: Unmute pending user {} not found.".format(ctx.message.author, user_id))
                embed = self.bot.basic_embed(False, "User **not found**!")

            await ctx.send(embed=embed)

    @commands.command()
    async def ban(self, ctx, user_id):
        if self.bot.is_mod(ctx.author):
            user_id = self.bot.mention_cleanup(user_id)
            try:
                ban_user = self.bot.senko_guild.get_member(int(user_id))
                if ban_user:
                    self.bot.send_log("Ban", "{}: Ban pending user {}({}) found: Banning.".format(
                        ctx.message.author, user_id, ban_user))
                    await self.bot.senko_guild.ban(ban_user)
                else:
                    fake_member = discord.Object(id=int(user_id))
                    await self.bot.senko_guild.ban(fake_member)
                    self.bot.send_log("Ban", "{}: Ban pending user {}({}) not found in server: Fake Banning.".format(
                        ctx.message.author, user_id, ban_user))

                embed = self.bot.basic_embed(True, "User **banned**!")
                await ctx.send(embed=embed)
            except (discord.NotFound, TypeError):
                self.bot.send_log("Ban", "{}: Ban pending user {} not found.".format(ctx.message.author, user_id))
                embed = self.bot.basic_embed(False, "User **not found**!")
                await ctx.send(embed=embed)

    @commands.command()
    async def unban(self, ctx, user_id):
        if self.bot.is_mod(ctx.author):
            user_id = self.bot.mention_cleanup(user_id)
            if get(self.bot.senko_guild.members, id=int(user_id)):
                embed = self.bot.basic_embed(False, "User is **not banned**!")
                await ctx.send(embed=embed)
            else:
                try:
                    fake_member = discord.Object(id=int(user_id))
                    await self.bot.senko_guild.unban(fake_member)
                    self.bot.send_log("Unban", "{}: Unban pending user {}({}) not found in server: Unbanning.".format(
                        ctx.message.author, user_id, fake_member))
                    embed = self.bot.basic_embed(True, "User **unbanned**!")
                    await ctx.send(embed=embed)
                except discord.NotFound:
                    self.bot.send_log("Unban", "{}: Unban pending user {} not found.".format(
                        ctx.message.author, user_id))
                    embed = self.bot.basic_embed(False, "User **not found**!")
                    await ctx.send(embed=embed)

    @commands.command()
    async def pingrole(self, ctx, role):
        if self.bot.is_mod(ctx.author):
            role = role.lower()
            if role == "server" or role == "s":
                role = self.bot.roles.news_server
            elif role == "anime" or role == "a":
                role = self.bot.roles.news_anime
            else:
                embed = self.bot.basic_embed(False, "Role {} **not found**!".format(role))
                await ctx.send(embed=embed)
                return
            await ctx.message.delete()
            await role.edit(mentionable=True)
            await ctx.send(content=role.mention)
            await role.edit(mentionable=False)
            await ctx.send("** **")

    @commands.command()
    async def mrf(self, ctx):
        if self.bot.is_mod(ctx.author):
            loading = discord.Embed(
                title=":hourglass:  **Refreshing** embeds for *#24h*  channel...",
                timestamp=ctx.message.created_at,
                color=0xffa749
            )
            msg = await ctx.send(embed=loading)
            await msg.edit(embed=loading)
            await self.bot.refresh_24h()
            embed = discord.Embed(
                title=":white_check_mark:  **Refreshed** embeds for *#24h*  channel!",
                timestamp=ctx.message.created_at,
                color=0x89af5b
            )
            await msg.edit(embed=embed)

    @commands.command()
    async def track(self, ctx, aid):
        if self.bot.is_mod(ctx.author):
            if aid == "-l":
                desc = "─────────────────"
                for i in self.bot.tracking:
                    title_name = None
                    animeid = None
                    for key, value in i.items():
                        animeid = key
                        for k, v in value.items():
                            title_name = v

                    if len(title_name) >= 41:
                        title_name = title_name[:40].strip() + "..."
                    str_to_add = "\n`{}` - {}".format(str(animeid).rjust(6, "0"), title_name)
                    desc += str_to_add
                embed = discord.Embed(
                    title=":notepad_spiral: **Currently tracking anime:**",
                    description=desc,
                    color=0xcdd4db,
                    timestamp=datetime.utcnow()
                )
                await ctx.send(embed=embed)
            else:
                data = await find_anime_by_id(aid)
                if data:
                    duplicate = False
                    if self.bot.tracking:
                        for i in self.bot.tracking:
                            for key, value in i.items():
                                if str(key) == str(data["id"]):
                                    duplicate = True
                    title = data["title"]["romaji"]
                    if not duplicate:
                        is_releasing = False
                        status = data["status"]
                        if status.lower() == "releasing":
                            is_releasing = True
                        else:
                            try:
                                x = data["airingSchedule"]["edges"][0]["node"]["episode"]
                                if x:
                                    is_releasing = True
                            except (IndexError, KeyError):
                                embed = self.bot.basic_embed(
                                    False, "__{}__ **not currently releasing**!".format(data["title"]["romaji"]))
                                await ctx.send(embed=embed)
                                return
                        if is_releasing:
                            to_append = {
                                str(data["id"]): {
                                    "title": title
                                }
                            }
                            await self.bot.append_tracking(to_append)
                            self.bot.send_log("Tracking", "Started tracking {} ({}) by {}".format(
                                title, data["id"], ctx.author))
                            embed = self.bot.basic_embed(True, "Started tracking **{}**!".format(title))
                        else:
                            embed = self.bot.basic_embed(
                                False, "__{}__ **not currently releasing**!".format(data["title"]["romaji"]))
                    else:
                        embed = self.bot.basic_embed(False, "Already tracking **{}**!".format(title))
                else:
                    embed = self.bot.basic_embed(False, "No anime with ID **{}** found!".format(aid))
                    embed.set_footer(text="Use !anime <name> -id to get the anilist ID.")
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ModsCog(bot))
