from discord.ext import commands
from datetime import datetime

from bot import Shiro
from util import strfdelta


class CmdCog(commands.Cog):
    def __init__(self, bot: Shiro):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(content="Ping!")


def setup(bot):
    bot.add_cog(CmdCog(bot))
