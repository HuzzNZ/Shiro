from discord.ext import commands
from discord.utils import get
import discord

from bot import Shiro
from util import build_embed
from util import build_manga_embed
from util import build_next_ep_embed
from idol_api import Idol

from anilist_api import find_anime_by_id
from anilist_api import find_anime_by_name
from anilist_api import find_manga_by_id
from anilist_api import find_manga_by_name

from math import floor
import math
import random


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
                embed = self.bot.basic_embed(False, "Title __{}__ **not found**!".format(anime_id))
            else:
                embed = return_data[0]
            await ctx.send(embed=embed)
        else:
            if not data:
                embed = self.bot.basic_embed(False, "Title __{}__ **not found**!".format(anime_id))
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
                embed = self.bot.basic_embed(False, "Title __{}__ **not found**!".format(manga_id))
            else:
                embed = return_data[0]
            await ctx.send(embed=embed)
        else:
            if not data:
                embed = self.bot.basic_embed(False, "Title __{}__ **not found**!".format(manga_id))
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
            embed = self.bot.basic_embed(False, "Title __{}__ **not found**!".format(anime_id))
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
                    embed = self.bot.basic_embed(
                        False, "__{}__ **not currently releasing**!".format(data["title"]["romaji"])
                    )
        if fetch_embed:
            new_data = await build_next_ep_embed(data)
            embed = new_data[0]
        await ctx.send(embed=embed)

    @commands.command()
    async def waifu(self, ctx, wid=None):
        if not wid:
            num = floor(random.random() * 100000)
        else:
            num = int(wid)
        embed = discord.Embed()
        embed.add_field(name="**This waifu is not real**", value="**#{}**".format(num))
        embed.set_image(url="https://www.thiswaifudoesnotexist.net/example-{}.jpg".format(num))
        embed.set_author(name="StyleGAN by Gwern Branwen", url="https://www.gwern.net/")
        embed.set_footer(icon_url=self.bot.user.avatar_url, text="Random Waifu - requested by {}".format(
            ctx.author
        ))
        await ctx.send(embed=embed)

    @commands.command()
    async def dice(self, ctx, side=None):
        if side:
            err_message = ""
            try:
                side = int(side)
                if side > 999999999:
                    err_message = "Number cannot be larger than **1,000,000,000**!"
                    raise ValueError
            except ValueError:
                if not err_message:
                    err_message = "**{}** is not a valid number!".format(side)
                embed = self.bot.basic_embed(False, err_message)
                await ctx.send(embed=embed)
                return
        else:
            side = 6

        random_roll = math.ceil(random.random() * float(side))
        embed = discord.Embed(
            title=":game_die:  You rolled a **{}**!".format(random_roll),
            color=0xcc606d
        )
        embed.set_footer(
            text="{}-sided dice roll - requested by {}".format(side, ctx.author)
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def cointoss(self, ctx):
        random_choice = math.ceil(random.random() * 2.0)
        choice = None
        emoji = None
        color = None
        if random_choice == 1:
            choice = "Heads"
            emoji = ":dvd:"
            color = 0xf4d887
        elif random_choice == 2:
            choice = "Tails"
            emoji = ":cd:"
            color = 0x8c97a3
        embed = discord.Embed(
            title="{}  You tossed **{}**!".format(emoji, choice),
            color=color
        )
        embed.set_footer(
            text="Cointoss - requested by {}".format(ctx.author)
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def members(self, ctx):
        members = list(ctx.guild.members)
        bot_user = 0
        reg_user = 0
        for i in members:
            if i.bot:
                bot_user += 1
            else:
                reg_user += 1

        await ctx.send(":small_blue_diamond: Currently in the server:\n        **{}** Members + **{}** Bots".format(
            reg_user, bot_user))

    @commands.command()
    async def mywaifu(self, ctx, opt: str = None, *waifu_name: str):
        if not opt:
            list_roles = ctx.author.roles
            has_waifu = False
            self_waifu = None
            if list_roles[1] < self.bot.roles.waifu_start:
                has_waifu = True
                self_waifu = list_roles[1]
            if has_waifu:
                embed = discord.Embed(
                    title=":heart:  Your waifu is **{}**!".format(self_waifu.name),
                    description="",
                    color=0xbe1931
                )
                embed.set_footer(text="Use !help mywaifu for more information on the command.")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=":broken_heart:  **You don't currently have a waifu!**",
                    description="",
                    color=0xe75a70
                )
                embed.set_footer(text="Use !help mywaifu for more information on the command.")
                await ctx.send(embed=embed)
            return
        opt = opt.lower()
        name = ""
        if waifu_name:
            for part in waifu_name:
                name += part
                name += " "
            name = name.strip()
        else:
            pass
        blacklist = [
            "nigga", "nibba", "nigger", "gay", "anus", "penis", "vagina", "faggot", "fag", "tranny",
            "kirino from oreimo"
        ]
        inappropriate = False
        for word in blacklist:
            if word in name.lower():
                inappropriate = True
                break
        if inappropriate:
            embed = discord.Embed(
                title=":no_entry:  **I don't think that's an appropriate name...**",
                description="Try again with a different name.",
                color=self.bot.color_bad
            )
            await ctx.send(embed=embed)
            return
        if opt == "is" or opt == "add":
            if name.__len__() > 24:
                embed = discord.Embed(
                    title=":no_entry:  Your waifu's name is **too long**!",
                    description="Currently **{}**/24 chars.".format(name.__len__()),
                    color=self.bot.color_bad
                )
                await ctx.send(embed=embed)
                return
            else:
                list_roles = ctx.author.roles
                has_waifu = False
                self_waifu = None
                if list_roles[1] < self.bot.roles.waifu_start:
                    has_waifu = True
                    self_waifu = list_roles[1]
                if has_waifu:
                    embed = discord.Embed(
                        title=":no_entry:  **You already have a waifu!**",
                        description="Please be loyal to **{}**.".format(self_waifu.name),
                    )
                    embed.set_footer(text="Use !mywaifu isnow <name> to change your waifu.")
                    await ctx.send(embed=embed)
                else:
                    await self.bot.add_waifu_role(name, ctx)
                    list_messages = [
                        "Treat her well",
                        "Be nice to her",
                        "Be loyal",
                    ]
                    embed = discord.Embed(
                        title=":white_check_mark:  Waifu **{}** added!".format(name),
                        description="{}, {}.".format(random.choice(list_messages), ctx.message.author.mention),
                        color=self.bot.color_good
                    )
                    await ctx.send(embed=embed)
        elif opt == "isnow" or opt == "edit" or opt == "change" or opt == "changeto":
            if name.__len__() > 24:
                embed = discord.Embed(
                    title=":no_entry:  Your waifu's name is **too long**!",
                    description="Currently **{}**/24 chars.".format(name.__len__()),
                    color=self.bot.color_bad
                )
                await ctx.send(embed=embed)
                return
            else:
                list_roles = ctx.message.author.roles
                has_waifu = False
                if list_roles[1] < self.bot.roles.waifu_start:
                    has_waifu = True
                if not has_waifu:
                    embed = discord.Embed(
                        title=":no_entry:  **You don't have a waifu yet!**",
                        description="",
                        color=self.bot.color_bad
                    )
                    embed.set_footer(text="Use !mywaifu is <name> to add her.")
                    await ctx.send(embed=embed)
                    return
                else:
                    old_waifu = ctx.author.roles[1].name
                    await self.bot.delete_waifu_role(ctx.message.author.roles[1], ctx)
                    await self.bot.add_waifu_role(name, ctx)
                    list_messages = [
                        "For {} to be replaced by someone like her.. *sobs*",
                        "It.. It's not like {} wanted to be your waifu or anything!",
                        "Goodbye. {} won't ever miss you."
                    ]
                    embed = discord.Embed(
                        title=":white_check_mark:  Waifu changed to **{}**!".format(name),
                        description=random.choice(list_messages).format(old_waifu),
                        color=self.bot.color_good
                    )
                    await ctx.send(embed=embed)
        elif opt == "remove" or opt == "delete" or opt == "reset" or opt == "isnolonger":
            list_roles = ctx.message.author.roles
            has_waifu = False
            if list_roles[1] < self.bot.roles.waifu_start:
                has_waifu = True
            if not has_waifu:
                embed = discord.Embed(
                    title=":no_entry:  **You don't have a waifu yet!**",
                    description="",
                    color=self.bot.color_bad
                )
                embed.set_footer(text="Use !mywaifu is <name> to add her.")
                await ctx.send(embed=embed)
                return
            else:
                self_waifu = ctx.author.roles[1]
                await self.bot.delete_waifu_role(self_waifu, ctx)
                embed = discord.Embed(
                    title=":white_check_mark:  Waifu **Removed**.".format(name),
                    description="Goodbye forever, {}.".format(self_waifu),
                    color=self.bot.color_good
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=":no_entry:  Unknown Command!",
                description="",
                color=self.bot.color_bad
            )
            embed.set_footer(text="Use !help mywaifu for more information.")
            await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx: discord.ext.commands.Context, *user_input):
        if not user_input:
            user = ctx.author
        else:
            user = ""
            for i in user_input:
                user += i
                user += " "
            user = user.strip()
            members = ctx.guild.members
            if "@" in user:
                user_id = self.bot.mention_cleanup(user)
                user = get(members, id=user_id)
            else:
                try:
                    user_id = int(user)
                    user = get(members, id=user_id)
                except ValueError:
                    user_name = user
                    user = get(members, name=user_name)

        await self.bot.userinfo_embed(ctx, user)

    @commands.command()
    async def whois(self, ctx, *user_input):
        if not user_input:
            user = ctx.author
        else:
            user = ""
            for i in user_input:
                user += i
                user += " "
            user = user.strip()
            members = ctx.guild.members
            if "@" in user:
                user_id = self.bot.mention_cleanup(user)
                user = get(members, id=user_id)
            else:
                try:
                    user_id = int(user)
                    user = get(members, id=user_id)
                except ValueError:
                    user_name = user
                    user = get(members, name=user_name)

        await self.bot.userinfo_embed(ctx, user)

    @commands.command()
    async def help(self, ctx, cmd: str = None):
        if not cmd:
            doc_commands = ""
            for cmd in self.bot.docs.list_cmds:
                doc_commands += f"-  `!{cmd}`\n"
            embed = discord.Embed(
                title=":information_source:  **Main !help menu**",
                description="─────────────────\nBelow are a list of available commands.\n"
                            "Use `!help <command>` for more information!\n** **",
                color=0x3b88c3
            )
            embed.add_field(name="Commands", value=doc_commands)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
        else:
            cmd = cmd.lower().replace("!", "")
            if cmd == "8ball":
                cmd = "eightball"
            elif cmd == "userinfo" or cmd == "whois":
                cmd = "userinfo_whois"
            embed = getattr(self.bot.docs, cmd)

        embed.set_footer(
            icon_url=self.bot.user.avatar_url,
            text="{} - Made by {}.".format(self.bot.user, get(ctx.guild.members, id=338651890021826561))
        )
        await self.bot.send_docs(ctx, embed)

    @commands.command()
    async def idol(self, ctx, arg):
        async with ctx.channel.typing():
            idol = Idol()
            try:
                embed = await idol.get_random_embed(arg)
            except AttributeError:
                embed = self.bot.basic_embed(False, "Argument not found!")
                embed.set_footer(text="Use !help idol to get more information.")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CmdCog(bot))
