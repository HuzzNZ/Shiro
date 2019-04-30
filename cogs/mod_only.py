from discord.ext import commands
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
            await ctx.send(content=timedif)


def setup(bot):
    bot.add_cog(ModsCog(bot))
