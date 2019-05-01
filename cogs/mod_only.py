from discord.ext import commands
from discord.utils import get
import discord
from datetime import datetime

from bot import Shiro
from util import strfdelta


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
            embed = self.bot.basic_embed(True, "**{}** messages have been deleted!")
            message = await ctx.send(embed=embed)
            await message.delete(delay=10)
            self.bot.send_log(
                "Msg Purge",
                f"{ctx.message.author}: Purged {amount_deleted} messages in {ctx.message.channel} - "
                f"See list of purged messages below:\n")
            self.bot.send_log("Msg Purge", "====================================================================")
            for message in purge_list:
                user_name = f"{message.author}".ljust(18, " ")
                print(f"[{message.timestamp}] {user_name}: {message.content}")
            self.bot.send_log("Msg Purge", "====================================================================")

    @commands.command()
    async def echo(self, ctx, destination, *args):
        if self.bot.is_mod(ctx.author):
            message = ""
            for string in args:
                message += (string + " ")
            message = message.strip()
            dest_channel_id = destination.replace("<", "").replace(">", "").replace("#", "")
            dest_channel = get(ctx.guild.channels, id=int(dest_channel_id))
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
                        unmuted_user.remove_roles(self.bot.roles.muted)
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
        pass
        # if self.bot.is_mod(ctx.author):
        #     user_id = self.bot.mention_cleanup(user_id)
        #     try:
        #         ban_user = self.bot.senko_guild.get_member(int(user_id))
        #         if ban_user:
        #             self.bot.send_log("Ban", "{}: Ban pending user {}({}) found: Banning.".format(
        #                 ctx.message.author, user_id, ban_user))
        #             await self.bot.senko_guild.ban(ban_user)
        #         else:
        #             fake_member = discord.Object(id=int(user_id))
        #             await self.bot.senko_guild.ban(fake_member)
        #             self.bot.send_log("Ban", "{}: Ban pending user {}({}) not found in server: Fake Banning.".format(
        #                 ctx.message.author, user_id, ban_user))
        #
        #         embed = discord.Embed(
        #             title=":white_check_mark:  User **Banned**!",
        #             timestamp=ctx.message.timestamp,
        #             color=0x89af5b
        #         )
        #         await bot.say(embed=embed)
        #     except (discord.NotFound, TypeError):
        #         print("[Ban       ] {}: Ban pending user {} not found.".format(ctx.message.author, user_id))
        #         embed = discord.Embed(
        #             title=":no_entry:  User **not found**!",
        #             timestamp=ctx.message.timestamp,
        #             color=0xa22c34
        #         )
        #         await bot.say(embed=embed)


def setup(bot):
    bot.add_cog(ModsCog(bot))
