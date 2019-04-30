from discord.ext import commands
import discord

from bot import Shiro
from util import build_embed
from util import build_manga_embed
from util import build_next_ep_embed

from anilist_api import find_anime_by_id
from anilist_api import find_anime_by_name
from anilist_api import find_manga_by_id
from anilist_api import find_manga_by_name


class CmdCog(commands.Cog):
    def __init__(self, bot: Shiro):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(content=f"**Pong!** :ping_pong:")

    @commands.command()
    async def anime(self, ctx, *args):
        anime_id = ""
        get_id = False
        for i in args:
            if i == "-id":
                get_id = True
            else:
                anime_id += i
                anime_id += " "
        anime_id = anime_id.strip()
        try:
            anime_id = int(anime_id)
            data = await find_anime_by_id(anime_id)
        except ValueError:
            anime_name = anime_id
            data = await find_anime_by_name(anime_name)
        if not get_id:
            return_data = await build_embed(data)
            if not return_data:
                embed = discord.Embed(
                    title=":no_entry:  Title __{}__ **not found**!".format(anime_id),
                    timestamp=ctx.message.created_at,
                    color=0xa22c34
                )
            else:
                embed = return_data[0]
            await ctx.send(embed=embed)
        else:
            if not data:
                embed = discord.Embed(
                    title=":no_entry:  Title __{}__ **not found**!".format(anime_id),
                    timestamp=ctx.message.created_at,
                    color=0xa22c34
                )
            else:
                embed_color = data["coverImage"]["color"]
                if embed_color:
                    embed_color = embed_color.replace("#", "")
                else:
                    embed_color = "ffffff"

                embed = discord.Embed(
                    title="**{}**".format(data["title"]["romaji"]),
                    description="─────────────────",
                    color=int(embed_color, 16),
                    url=data["siteUrl"]
                )
                embed.set_thumbnail(url=data["coverImage"]["extraLarge"])
                embed.add_field(name="ID", value=data["id"])
            await ctx.send(embed=embed)

    @commands.command()
    async def manga(self, ctx, *args):
        manga_id = ""
        get_id = False
        for i in args:
            if i == "-id":
                get_id = True
            else:
                manga_id += i
                manga_id += " "
        manga_id = manga_id.strip()
        try:
            manga_id = int(manga_id)
            data = await find_manga_by_id(manga_id)
        except ValueError:
            manga_name = manga_id
            data = await find_manga_by_name(manga_name)
        if not get_id:
            return_data = await build_manga_embed(data)
            if not return_data:
                embed = discord.Embed(
                    title=":no_entry:  Title __{}__ **not found**!".format(manga_id),
                    timestamp=ctx.message.created_at,
                    color=0xa22c34
                )
            else:
                embed = return_data[0]
            await ctx.send(embed=embed)
        else:
            if not data:
                embed = discord.Embed(
                    title=":no_entry:  Title __{}__ **not found**!".format(manga_id),
                    timestamp=ctx.message.created_at,
                    color=0xa22c34
                )
            else:
                embed_color = data["coverImage"]["color"]
                if embed_color:
                    embed_color = embed_color.replace("#", "")
                else:
                    embed_color = "ffffff"

                embed = discord.Embed(
                    title="**{}**".format(data["title"]["romaji"]),
                    description="─────────────────",
                    color=int(embed_color, 16),
                    url=data["siteUrl"]
                )
                embed.set_thumbnail(url=data["coverImage"]["extraLarge"])
                embed.add_field(name="ID", value=data["id"])
            await ctx.send(embed=embed)

    @commands.command()
    async def nextep(self, ctx, *args):
        fetch_embed = False
        embed = None
        anime_id = ""
        for i in args:
            anime_id += i
            anime_id += " "
        anime_id = anime_id.strip()
        try:
            anime_id = int(anime_id)
            data = await find_anime_by_id(anime_id)
        except ValueError:
            anime_name = anime_id
            data = await find_anime_by_name(anime_name)
        return_data = await build_embed(data)
        if not return_data:
            embed = discord.Embed(
                title=":no_entry:  Title __{}__ **not found**!".format(anime_id),
                timestamp=ctx.message.created_at,
                color=0xa22c34
            )
        else:
            status = data["status"]
            if status.lower() == "releasing":
                fetch_embed = True
            else:
                try:
                    x = data["airingSchedule"]["edges"][0]["node"]["episode"]
                    if x:
                        fetch_embed = True
                except (IndexError, KeyError):
                    embed = discord.Embed(
                        title=":no_entry:  __{}__ **not currently releasing**!".format(data["title"]["romaji"]),
                        timestamp=ctx.message.created_at,
                        color=0xa22c34
                    )
        if fetch_embed:
            new_data = await build_next_ep_embed(data)
            embed = new_data[0]
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CmdCog(bot))
