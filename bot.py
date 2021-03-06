# Discord
import discord
from discord.ext import commands
from discord.utils import get
import logging


# Local Scripts
from apis.anilist_api import find_anime_by_id
from apis.anilist_api import find_anime_by_name
from apis.anilist_api import find_manga_by_name
from apis.reddit_api import Reddit
from util import build_next_ep_embed
from util import build_small_embed
from util import build_small_manga_embed
from util import build_translate_embed
from util import time_diff
from util import strfdelta
from docs import Docs


# Python Built-ins
from collections import namedtuple
import json
import os
from datetime import datetime
import sys
import random

# asyncio
import asyncio

# reddit & scheduler
import praw
import schedule


# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# Main Bot class definition
class Shiro(commands.Bot):
    def __init__(self):
        # Inheriting discord.Client class
        super().__init__(command_prefix="!")

        # Finding bot platform
        self.on_windows = sys.platform == "win32"

        # Finding bot script base directory
        self.base_path = os.path.abspath("bot.py")

        # Finding File Directories
        if self.on_windows or "shiro" in self.base_path:
            in_folder = ""
        else:
            in_folder = "shiro"

        self.const_file = self.base_path.replace("bot.py", os.path.join(in_folder, "constants.json"))
        self.track_file = self.base_path.replace("bot.py", os.path.join(in_folder, "tracking.json"))
        self.track_msg_file = self.base_path.replace("bot.py", os.path.join(in_folder, "tracking_msg.json"))

        # Finding Client Token
        self.cred_file = self.base_path.replace("bot.py", os.path.join(in_folder, ".creds.json"))
        self.creds = self.load_file(self.cred_file)
        self.token = self.creds["token"]
        self.osu = self.creds["osu"]

        # Finding Reddit Tokens
        self.reddit = praw.Reddit

        # Making room for custom help command
        self.remove_command("help")

        # Loading Docs
        self.docs = Docs()

        # Loading Constants
        self.constants = self.load_file(self.const_file)
        self.senko_guild = None
        self.channel_ids = dict
        self.channels = namedtuple("Channel", "roles release uptime logs pins docs staff_bot memes")
        self.role_ids = dict
        self.roles = namedtuple("Role", "kitsune member spacer_pings spacer_special "
                                        "news_server news_anime disc_anime disc_manga waifu_start waifu_end muted")

        # Loading Embed Colors
        self.color_bad = 0xa22c34
        self.color_good = 0x89af5b

        # Loading Pin Threshold
        self.pin_threshold = self.constants["pin_threshold"]

        # Loading Tracking Messages
        self.tracking = self.load_file(self.track_file)
        self.tracking_msgs = self.load_file(self.track_msg_file)

        # Adding Scheduler Events
        schedule.every().minute.do(self.async_wrapper_minutes)
        schedule.every().minute.at(":00").do(self.async_wrapper_embed)
        schedule.every().minute.at(":00").do(self.async_wrapper_presence)
        schedule.every(10).minutes.do(self.async_wrapper_roles)
        schedule.every().hour.at(":00").do(self.async_wrapper_24h)
        schedule.every().hour.at(":30").do(self.async_wrapper_24h)
        schedule.every().day.at("10:45:00").do(self.async_wrapper_meme)

        # Starting the bot
        self.send_log("Bot Client", "Starting process")
        self.ontime_loop = None

        self.start_time = datetime.utcnow()
        self.load_extension("cogs.commands")
        self.load_extension("cogs.mod_only")
        self.run(self.token)

    @staticmethod
    def send_log(title: str, message: str):
        title = title.ljust(10, " ")
        print(f"[{datetime.utcnow()}][{title}] {message}")

    @staticmethod
    def load_file(file_dir):
        with open(file_dir, "r", encoding="UTF-8") as file:
            return json.loads(file.read())

    @staticmethod
    def mention_cleanup(input_str):
        return int(input_str.replace("<", "").replace("@", "").replace("!", "").replace(">", ""))

    def basic_embed(self, is_tick: bool = True, message: str = None):
        if is_tick:
            color = self.color_good
            title_prefix = ":white_check_mark:"
        else:
            color = self.color_bad
            title_prefix = ":no_entry:"

        embed = discord.Embed(
            title="{}  {}".format(title_prefix, message),
            timestamp=datetime.utcnow(),
            color=color
        )
        return embed

    def has_base_roles(self, member: discord.Member):
        base_roles = [
            self.roles.member,
            self.roles.spacer_pings,
            self.roles.spacer_special
        ]

        has_roles = False
        for role in base_roles:
            owned = get(member.roles, id=role.id)
            if owned:
                has_roles = True
            else:
                has_roles = False
                break

        return has_roles

    def is_mod(self, member: discord.Member):
        owned = get(member.roles, id=self.roles.kitsune.id)
        if owned:
            return True
        return False

    async def append_tracking(self, dict_):
        self.tracking.append(dict_)
        with open(self.track_file, "w", encoding="UTF-8") as writefile:
            json.dump(self.tracking, writefile)

    async def define_constants(self):
        self.senko_guild = self.get_guild(int(self.constants['guild']))

        # Loading Channels
        self.channel_ids = self.constants["channels"]
        Channel = namedtuple("Channel", "roles release uptime logs pins docs staff_bot memes")

        roles = self.get_channel(id=int(self.channel_ids["roles"]))
        release = self.get_channel(id=int(self.channel_ids["release"]))
        uptime = self.get_channel(id=int(self.channel_ids["uptime"]))
        logs = self.get_channel(id=int(self.channel_ids["logs"]))
        pins = self.get_channel(id=int(self.channel_ids["pins"]))
        docs = self.get_channel(id=int(self.channel_ids["docs"]))
        staff_bot = self.get_channel(id=int(self.channel_ids["staff-bot"]))
        memes = self.get_channel(id=int(self.channel_ids["memes"]))

        self.channels = Channel(roles, release, uptime, logs, pins, docs, staff_bot, memes)

        # Loading Roles
        self.role_ids = self.constants["roles"]
        Role = namedtuple("Role", "kitsune member spacer_pings spacer_special "
                                  "news_server news_anime disc_anime disc_manga waifu_start muted")

        kitsune = get(self.senko_guild.roles, id=int(self.role_ids["kitsune"]))
        member = self.senko_guild.get_role(int(self.role_ids["member"]))
        spacer_pings = self.senko_guild.get_role(int(self.role_ids["spacer-pings"]))
        spacer_special = self.senko_guild.get_role(int(self.role_ids["spacer-special"]))
        news_server = get(self.senko_guild.roles, id=int(self.role_ids["news-server"]))
        news_anime = get(self.senko_guild.roles, id=int(self.role_ids["news-anime"]))
        disc_anime = get(self.senko_guild.roles, id=int(self.role_ids["disc-anime"]))
        disc_manga = get(self.senko_guild.roles, id=int(self.role_ids["disc-manga"]))
        waifu_start = get(self.senko_guild.roles, id=int(self.role_ids["waifu-start"]))
        muted = get(self.senko_guild.roles, id=int(self.role_ids["muted"]))

        self.roles = Role(kitsune, member, spacer_pings, spacer_special, news_server, news_anime, disc_anime,
                          disc_manga, waifu_start, muted)

        # Logging into Reddit
        reddit_creds = self.creds["reddit"]

        client_id = reddit_creds["client_id"]
        client_secret = reddit_creds["client_secret"]
        r_password = reddit_creds["password"]
        user_agent = reddit_creds["user_agent"]
        username = reddit_creds["username"]

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=r_password,
            user_agent=user_agent,
            username=username
        )
        self.send_log("...", "Logged into Reddit as {}".format(self.reddit.user.me()))

    # ======================== #
    #                          #
    # ######## ONTIME ######## #
    #                          #
    # ======================== #

    async def check_releasing(self, aid, data=None):
        if not data:
            data = await find_anime_by_id(aid)
        status = data["status"]
        if status.lower() == "releasing":
            return True, data
        else:
            try:
                if data["airingSchedule"]["edges"][0]["node"]["episode"]:
                    return True, data
            except (IndexError, KeyError):
                self.send_log("24h Check", "{} has finished releasing.".format(data["title"]["romaji"]))
                return False, data

    async def del_msg_json(self, msg_id):
        counter = 0
        for i in self.tracking_msgs:
            if str(i["msg_id"]) == str(msg_id):
                self.send_log("24h del", "Deleted message ID {} (\"{}\" Episode {}).".format(i["msg_id"], i["id"],
                                                                                             i["episode"]))
                break
            counter += 1
        del self.tracking_msgs[counter]
        with open(self.track_msg_file, "w", encoding="utf-8") as wf:
            json.dump(self.tracking_msgs, wf)

    async def add_msg_json(self, msg_dict):
        self.tracking_msgs.append(msg_dict)
        with open(self.track_msg_file, "w", encoding="utf-8") as wf:
            json.dump(self.tracking_msgs, wf)

    async def refresh_24h(self):
        counter = 0
        aid = None
        for entry in self.tracking:
            for key, value in entry.items():
                aid = key

            is_releasing, data = await self.check_releasing(aid)
            if is_releasing:
                if data:
                    try:
                        airing_node = data["airingSchedule"]["edges"][0]['node']
                        time = airing_node["airingAt"]
                    except (IndexError, KeyError):
                        continue
                    if "d" not in await time_diff(datetime.utcfromtimestamp(time), datetime.utcnow()):
                        duplicate = False
                        if self.tracking_msgs:
                            for item in self.tracking_msgs:
                                try:
                                    if str(aid) == str(item["id"]):
                                        duplicate = True
                                except KeyError:
                                    pass
                        if duplicate:
                            pass
                        else:
                            embed = await build_next_ep_embed(data)
                            embed = embed[0]
                            message = await self.channels.release.send(embed=embed)
                            append_data = {
                                "msg_id": message.id,
                                "id": aid,
                                "epoch": time,
                                "episode": airing_node["episode"]
                            }
                            await self.add_msg_json(append_data)
                            self.send_log("24h gen", "Generated Embeds for: \"{}\" [Episode {}] ({})".format(
                                data["title"]["romaji"], airing_node["episode"], aid))
            else:
                del self.tracking[counter]
            counter += 1

        with open(self.track_file, "w", encoding="utf-8") as wf:
            json.dump(self.tracking, wf)

    def async_wrapper_24h(self):
        asyncio.run_coroutine_threadsafe(self.refresh_24h(), self.loop)

    async def refresh(self):
        counter = 0
        for entry in self.tracking_msgs:
            msg = None
            message_id = entry["msg_id"]
            entry_id = entry["id"]
            epoch = entry["epoch"]
            episode = entry["episode"]
            find_msg_success = False
            for attempt in range(10):
                try:
                    msg = await self.channels.release.fetch_message(id=int(message_id))
                    find_msg_success = True
                except AttributeError:
                    find_msg_success = True
                    break
                except Exception as error:
                    if str(error).lower() == "session is closed":
                        find_msg_success = True
                        break
                    self.send_log("24h err", "({}) {}".format(attempt + 1, str(error)))
                    await asyncio.sleep(0.5)
                    continue
                break
            if not find_msg_success:
                self.send_log("DEBUG", "Message delete (code 101)")
                await self.del_msg_json(message_id)
                continue

            data = await find_anime_by_id(entry_id)
            embed = await build_next_ep_embed(data, epoch, episode)
            if embed:
                await msg.edit(embed=embed[0])
                continue

            data = await find_anime_by_id(entry_id)
            title = data["title"]["romaji"]
            site_url = data["siteUrl"]
            desc = "─────────────────\n" + data["description"].split("<br>")[0].replace("<i>", "").replace("</i>", "")
            if len(desc) >= 141:
                desc = desc[:140].strip() + "... [read more]({})".format(site_url)
            else:
                desc += (140 - len(desc)) * " "
                desc += "** **"

            embed = discord.Embed(
                title=f"**{title}**",
                description=desc,
                url=site_url,
                color=0xbd3d45,
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=data["coverImage"]["extraLarge"])
            embed.add_field(name="** **", value=f":red_circle: **Episode {episode}** has **Aired**.",
                            inline=False)
            await msg.edit(embed=embed)
            await self.del_msg_json(message_id)
            self.send_log("24h air", "Updated Embeds for: \"{}\" [Episode {}] ({}) - New Episode AIRED.".format(
                title, episode, entry_id))
            counter += 1

    def async_wrapper_embed(self):
        asyncio.run_coroutine_threadsafe(self.refresh(), self.loop)

    async def gen_role_embeds(self):
        try:
            message = None
            messages = self.channels.roles.history(limit=1)
            async for i in messages:
                message = i
            await message.delete()
        except Exception as error:
            self.send_log("GRE Error", str(error))
        server_embed = discord.Embed(
            color=self.color_good,
            title="**React below to select your roles!**",
            description="─────────────────\n:newspaper: - To Receive Pings for future Server News\n"
                        ":flag_jp: - To Receive Pings for future Anime News\n"
                        "** **\n"
                        ":regional_indicator_a: - To indicate that you are open to Senko-san Anime Discussions\n"
                        ":regional_indicator_m: - To indicate that you are open to Senko-san Manga Discussions"
        )
        server_embed_msg = await self.channels.roles.send(embed=server_embed)
        await server_embed_msg.add_reaction("📰")
        await server_embed_msg.add_reaction("🇯🇵")
        await server_embed_msg.add_reaction("🇦")
        await server_embed_msg.add_reaction("🇲")

    async def refresh_roles(self):
        for member in self.senko_guild.members:
            if not self.has_base_roles(member) and not member.bot:
                await member.add_roles(self.roles.spacer_special)
                await member.add_roles(self.roles.spacer_pings)
                await member.add_roles(self.roles.member)

    def async_wrapper_roles(self):
        asyncio.run_coroutine_threadsafe(self.refresh_roles(), self.loop)

    async def refresh_presence(self):
        currently_playing = discord.Game(name=f"{'with {} users!'.format(len(self.senko_guild.members))}  ·  !help")
        await self.change_presence(activity=currently_playing)

    def async_wrapper_presence(self):
        asyncio.run_coroutine_threadsafe(self.refresh_presence(), self.loop)

    async def send_meme(self):
        reddit = Reddit(self.reddit)
        await reddit.get_random_animeme()
        await reddit.check_for_video()
        embed = await reddit.get_embed()
        await self.channels.memes.send(embed=embed)

    def async_wrapper_meme(self):
        asyncio.run_coroutine_threadsafe(self.send_meme(), self.loop)

    async def send_minutes(self):
        timedif = strfdelta(datetime.utcnow() - self.start_time)
        await self.channels.uptime.send(f":large_blue_circle: I have been up for **{timedif}**.")

    def async_wrapper_minutes(self):
        asyncio.run_coroutine_threadsafe(self.send_minutes(), self.loop)

    async def on_time_loop(self):
        await self.wait_until_ready()
        await self.define_constants()
        await self.channels.uptime.send(content=":red_circle: **I have just been rebooted!**")
        self.send_log("...", "Refreshing 24h")
        await self.refresh_24h()
        self.send_log("...", "Refreshing Embeds")
        await self.refresh()
        self.send_log("...", "Refreshing Roles")
        await self.refresh_roles()
        self.send_log("...", "Refreshing Role Embeds")
        await self.gen_role_embeds()
        self.send_log("...", "Refreshing Presence")
        await self.refresh_presence()
        self.send_log("...", "!! Startup Process Finished !!")
        while True:
            try:
                await asyncio.sleep(0.5)
                schedule.run_pending()
            except KeyboardInterrupt:
                return
            except Exception as error:
                self.send_log("Ontime Err", str(error))

    # ======================== #
    #                          #
    # ###### BOT EVENTS ###### #
    #                          #
    # ======================== #

    async def on_ready(self):
        await self.on_time_loop()
        self.send_log("Bot Client", "Ready on Discord")

    async def on_message(self, message: discord.Message):
        content = message.content
        if "discord.gg" in content:
            if not get(message.author.roles, id=self.roles.kitsune.id):
                await message.delete()
                await self.channels.staff_bot.send(
                    content=f"{message.author.mention} just tried to post this invite "
                    f"link in {message.channel}: {message.content}"
                )
            return
        if "--Literal" in content or "--l" in content:
            pass

        elif "{" in content and "}" in content:
            try:
                to_find_list = []
                for i in range(len(content)):
                    if content[i] == "{":
                        back_brace = content.find("}", i)
                        if not back_brace == -1:
                            to_find_list.append([i, back_brace])
                            if len(to_find_list) >= 3:
                                break
            except IndexError:
                return
            if to_find_list:
                for i in to_find_list:
                    start = i[0] + 1
                    end = i[1]
                    if not start == end:
                        to_find = content[start:end]
                    else:
                        return
                    if "{" not in to_find or "}" not in to_find:
                        data = await find_anime_by_name(to_find)
                        return_data = await build_small_embed(data)
                        if not return_data:
                            self.send_log("Anime {Qry", "{} - Queried \"{}\" to Anilist.co (USING BRACKETS), "
                                          "not found!".format(message.author, to_find))
                            embed = self.basic_embed(False, "Title __{}__ **not found**!".format(content))
                        else:
                            embed = return_data[0]
                            self.send_log("Anime {Qry", "{} - Queried \"{}\" to Anilist.co (USING BRACKETS), "
                                          "returned {}".format(message.author, to_find, return_data[1]))
                        await message.channel.send(embed=embed)

        elif "[" in content and "]" in content:
            try:
                to_find_list = []
                for i in range(len(content)):
                    if content[i] == "[":
                        back_brace = content.find("]", i)
                        if not back_brace == -1:
                            to_find_list.append([i, back_brace])
                            if len(to_find_list) >= 3:
                                break
            except IndexError:
                return
            if to_find_list:
                for i in to_find_list:
                    start = i[0] + 1
                    end = i[1]
                    if not start == end:
                        to_find = content[start:end]
                    else:
                        return
                    if "[" not in to_find or "]" not in to_find:
                        data = await find_manga_by_name(to_find)
                        self.send_log("Manga [Qry", "{} - Queried \"{}\" to Anilist.co (USING BRACKETS), "
                                                    "not found!".format(message.author, to_find))
                        return_data = await build_small_manga_embed(data)
                        if not return_data:
                            print("not found!")
                            embed = self.basic_embed(False, "Title __{}__ **not found**!".format(content))
                        else:
                            embed = return_data[0]
                            self.send_log("Manga [Qry", "{} - Queried \"{}\" to Anilist.co (USING BRACKETS), "
                                          "returned {}".format(message.author, to_find, return_data[1]))
                        await message.channel.send(embed=embed)

        elif content.split(" ")[0] == "!8ball":
            question = ""
            for i in content.split(" "):
                if not i == "!8ball":
                    question += i
                    question += " "
            question = question.strip()
            await self.magic8(message, question)

        elif ">>" in content:
            to_translate = None
            if content == "^ >>":
                messageable = message.channel
                async for msg in messageable.history(limit=2):
                    if not message == msg:
                        to_translate = msg.content
            else:
                notation_place = content.find(" >>")
                if content[notation_place - 1] == content[-4]:
                    to_translate = content[:notation_place]
            if to_translate:
                async with message.channel.typing():
                    embed = await build_translate_embed(to_translate)
                    embed.set_footer(text=f"JP to EN Translation | Requested by {message.author}",
                                     icon_url=self.user.avatar_url)
                    await message.channel.send(embed=embed)

        else:
            try:
                await self.process_commands(message)
            except discord.ext.commands.errors.CommandNotFound:
                embed = self.basic_embed(False, "Command **{}** not found!".format(
                    message.content.split(" ")[0].replace("!", "")))
                embed.set_footer(text='!help to see a list of all available commands.')
                cmd_not_found_msg = await message.channel.send(embed=embed)
                await cmd_not_found_msg.delete(delay=5)

    async def on_member_join(self, member):
        # Adding Member Role
        self.send_log("User Join", f"{member}({member.id}) joined.")
        await member.add_roles(self.roles.member, self.roles.spacer_pings, self.roles.spacer_special)

        # server-logs message
        embed = discord.Embed(
            title=":door:  **{}#{}** joined the server.".format(member.name, member.discriminator),
            description="** **",
            color=0x99cc99,
            timestamp=member.joined_at
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Account created at:", value=str(member.created_at) + " ({} ago)".format(
            await time_diff(datetime.utcnow(), member.created_at)), inline=False)
        embed.add_field(name="User ID:", value=f"{member.mention} {member.id}", inline=False)

        await self.channels.logs.send(embed=embed)

    async def on_member_remove(self, member):
        # server-logs message
        self.send_log("User Leave", f"{member}({member.id}) left.")

        embed = discord.Embed(
            title=":no_entry_sign:  **{}#{}**  left the server after **{}**.".format(
                member.name,
                member.discriminator,
                strfdelta(datetime.utcnow() - member.joined_at)
            ),
            description="** **",
            color=0xcc9999,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="User ID:", value=f"{member.mention} {member.id}", inline=False)

        await self.channels.logs.send(embed=embed)

    async def on_message_edit(self, before, after):
        member = before.author
        if after.content and before.content and not after.content == before.content:
            self.send_log(
                "Msg Edit",
                f"{member}({member.id}) edited message in #{before.channel.name}:\n"
                f"                 {before.content}\n"
                f"              -> {after.content}"
            )
            embed = discord.Embed(
                title=":information_source:  **{}#{}**  Edited message:".format(member.name, member.discriminator),
                description="** **",
                color=0x999999,
                timestamp=after.created_at
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="Before:", value=before.content, inline=False)
            embed.add_field(name="After:", value=after.content, inline=False)
            embed.add_field(name="In:", value=f'<#{before.channel.id}>', inline=False)
            embed.add_field(name="User ID:", value=f"{after.author.mention} {after.author.id}", inline=False)

            await self.channels.logs.send(embed=embed)

    async def on_message_delete(self, message):
        member = message.author
        self.send_log(
            "Msg Delete",
            f"[Msg Del   ] {member}({member.id}) deleted message in #{message.channel.name}:\n"
            f"               - {message.content}")
        embed = discord.Embed(
            title=":information_source:  **{}#{}**  Deleted message:".format(member.name, member.discriminator),
            description="** **",
            color=0x999999,
            timestamp=message.created_at
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Content:", value=message.content, inline=False)
        embed.add_field(name="In:", value=f'<#{message.channel.id}>', inline=False)
        embed.add_field(name="User ID:", value=f"{member.mention} {message.author.id}", inline=False)

        await self.channels.logs.send(embed=embed)

    async def on_reaction_add(self, reaction, user):
        if not user.bot:
            if reaction.emoji == "📌":
                self.send_log("Pinboard", "Pin reaction found")
                has_pin = False
                message = reaction.message
                for reaction in message.reactions:
                    if reaction.emoji == "📌":
                        if reaction.count > 1:
                            has_pin = True
                            break
                if not has_pin:
                    await self.pin_loop(message)

            elif reaction.emoji == "📰":
                if reaction.message.channel == self.channels.roles:
                    await user.add_roles(self.roles.news_server)
                    self.send_log("Role Rxn +", "Added Server News to {} ({})".format(user, user.id))

            elif reaction.emoji == "🇯🇵":
                if reaction.message.channel == self.channels.roles:
                    await user.add_roles(self.roles.news_anime)
                    self.send_log("Role Rxn +", "Added Anime News to {} ({})".format(user, user.id))

            elif reaction.emoji == "🇦":
                if reaction.message.channel == self.channels.roles:
                    await user.add_roles(self.roles.disc_anime)
                    self.send_log("Role Rxn +", "Added Anime Disc to {} ({})".format(user, user.id))

            elif reaction.emoji == "🇲":
                if reaction.message.channel == self.channels.roles:
                    await user.add_roles(self.roles.disc_manga)
                    self.send_log("Role Rxn +", "Added Manga Disc to {} ({})".format(user, user.id))

    async def on_reaction_remove(self, reaction, user):
        if not user.bot:
            if reaction.emoji == "📰":
                if reaction.message.channel == self.channels.roles:
                    await user.remove_roles(self.roles.news_server)
                    self.send_log("Role Rxn -", "Removed Server News from {} ({})".format(user, user.id))

            elif reaction.emoji == "🇯🇵":
                if reaction.message.channel == self.channels.roles:
                    await user.remove_roles(self.roles.news_anime)
                    self.send_log("Role Rxn -", "Removed Anime News from {} ({})".format(user, user.id))

            elif reaction.emoji == "🇦":
                if reaction.message.channel == self.channels.roles:
                    await user.remove_roles(self.roles.disc_anime)
                    self.send_log("Role Rxn -", "Removed Anime Disc from {} ({})".format(user, user.id))

            elif reaction.emoji == "🇲":
                if reaction.message.channel == self.channels.roles:
                    await user.remove_roles(self.roles.disc_manga)
                    self.send_log("Role Rxn -", "Removed Manga Disc from {} ({})".format(user, user.id))

    # ======================== #
    #                          #
    # ######### UTIL ######### #
    #                          #
    # ======================== #

    async def pin_loop(self, message):
        msg_channel = message.channel
        pin_count = 0
        pinned = False
        self.send_log("Pinboard", "Pin tracking on message \"{}\"".format(message.content))
        embed = discord.Embed(
            title=":pushpin:  Pinboard vote **Initiated**.",
            description="**{}**/**{}**".format(1, self.pin_threshold),
            timestamp=message.created_at,
            color=0xbd3d45
        )
        embed_msg = await msg_channel.send(embed=embed)
        if not message.content:
            content = "*`<No content>`*"
        else:
            content = message.content

        for i in range(0, 600):
            await asyncio.sleep(0.05)
            message = await msg_channel.fetch_message(id=message.id)
            message_reactions = message.reactions
            for reaction in message_reactions:
                if reaction.emoji == "📌":
                    pc_now = pin_count
                    pin_count = reaction.count
                    if pc_now != pin_count:
                        self.send_log("Pinboard", "Another pin added on message \"{}\", now {}".format(
                            content, pin_count))
                        if pin_count >= self.pin_threshold:
                            embed = discord.Embed(
                                title=":pushpin:  Pinboard vote **succeeded**!",
                                description="**{}**/**{}**".format(pin_count, self.pin_threshold),
                                timestamp=message.created_at,
                                color=self.color_good
                            )
                            await embed_msg.edit(embed=embed)
                            pinned = True
                            break
                        else:
                            embed = discord.Embed(
                                title=":pushpin:  Pinboard vote **Pending**:",
                                description="**{}**/**{}**".format(pin_count, self.pin_threshold),
                                timestamp=message.created_at,
                                color=0xffa749
                            )
                            await embed_msg.edit(embed=embed)
                else:
                    try:
                        await embed_msg.delete()
                        break
                    except Exception as error:
                        self.send_log("Pinboard e", str(error))
                        continue
            if pinned:
                break
            else:
                pinned = False
        if not pinned:
            embed = discord.Embed(
                title=":pushpin:  Pinboard vote **Failed**!",
                description="**{}**/**{}**".format(pin_count, self.pin_threshold),
                timestamp=message.created_at,
                color=0xbd3d45
            )
            await embed_msg.edit(embed=embed)
        else:
            self.send_log("Pinboard +", "({}) {}#{}: {} [{}]".format(
                pin_count, message.author.name, message.author.discriminator, content, message.created_at))
            has_embed = False
            embed_url = None
            if message.embeds:
                has_embed = True
                for i in message.embeds:
                    i = i.to_dict()
                    if i["type"] != "image":
                        has_embed = False
                    else:
                        embed_url = i["url"]
                        has_embed = True
                        break
            elif message.attachments:
                has_embed = True
                for i in message.attachments:
                    embed_url = i.url
                    break
            embed_title = "**Pinned message:**".format(message.channel.name)
            embed_desc = ":pushpin: **in** <#{}>:\n─────────────────\n<@{}>:".format(
                message.channel.id, message.author.id)
            embed = discord.Embed(
                title=embed_title,
                description=embed_desc,
                timestamp=message.created_at,
                color=0xbd3d45
            )
            embed.set_thumbnail(url=message.author.avatar_url)
            if has_embed:
                embed.set_image(url=embed_url)
                content = content.replace(embed_url, "*`<Embedded URL>`*")
            embed.add_field(name=content, value="** **")

            pin_msg = await self.channels.pins.send(content=f"**Jump to:** <{message.jump_url}>", embed=embed)
            if pin_msg:
                pass
            #
            # for i in range(0, 1800):
            #     await asyncio.sleep(1)
            #     msg_channel = message.channel
            #     message = await msg_channel.fetch_message(id=message.id)
            #     message_reactions = message.reactions
            #     for reaction in message_reactions:
            #         if reaction.emoji == "📌":
            #             pc_now = pin_count
            #             pin_count = reaction.count
            #             if pc_now != pin_count:
            #                 self.send_log("Pinboard", "Another pin added on message \"{}\", now {}".format(
            #                     content, pin_count))
            #
            #                 embed_desc = ":pushpin: **x {} ** in <#{}>:\n─────────────────\n<@{}>:".format(
            #                     pin_count,
            #                     message.channel.id,
            #                     message.author.id
            #                 )
            #                 embed = discord.Embed(
            #                     title=embed_title,
            #                     description=embed_desc,
            #                     timestamp=message.created_at,
            #                     color=0xbd3d45
            #                 )
            #                 embed.add_field(name=content, value="** **")
            #                 embed.set_thumbnail(url=message.author.avatar_url)
            #                 if has_embed:
            #                     embed.set_image(url=embed_url)
            #                 await pin_msg.edit(embed=embed)

    async def magic8(self, msg, question):
        replies = ["Definitely yes.",
                   "Perhaps.",
                   "Maybe yes?",
                   "Probably not.",
                   "That's a no.",
                   "Fuck no!",
                   "Ask again?",
                   "Not now.",
                   "In a week's time.",
                   "No doubt",
                   "I cannot tell you now.",
                   "Reply hazy... Try again later.",
                   "It's better you don't ask.",
                   "You even need to ask that?",
                   "If that's what you want.",
                   "I have no idea.",
                   "YES! YES! YES!",
                   "Please stop asking me."]
        random_choice = random.choice(replies)
        title = ":8ball:  **{}#{} summoned the 8-ball:**".format(msg.author.name, msg.author.discriminator)
        question = question.replace("?", "")
        description = "─────────────────\n⁣\nQ: {}?\nA: **{}**⁣".format(question, random_choice)

        embed = discord.Embed(
            title=title,
            description=description,
            color=0x6800d1
        )

        self.send_log("8 Ball", "{} Asked the 8 ball: {}".format(msg.author, question))
        await msg.channel.send(embed=embed)

    async def add_waifu_role(self, waifu_name, ctx):
        none_perms = discord.Permissions(0)
        new_role = await self.senko_guild.create_role(
            name=waifu_name,
            permissions=none_perms,
            color=discord.Colour(0x888888)
        )
        await new_role.edit(position=2)
        self.send_log("Role +", "Added role \"{}\" by {}".format(waifu_name, ctx.author))
        await ctx.author.add_roles(new_role)

    async def delete_waifu_role(self, waifu_role: discord.Role, ctx):
        await waifu_role.delete()
        self.send_log("Role -", "Deleted role \"{}\" by {}".format(waifu_role.name, ctx.message.author))

    async def userinfo_embed(self, ctx: discord.ext.commands.Context, user):
        if user:
            if user.nick:
                title = f":information_source:  **{user.nick}** AKA **{user.name}**:"
            else:
                title = f":information_source:  **{user.name}**:"

            acc_diff = await time_diff(datetime.utcnow(), user.created_at)
            account_creation = f"{user.created_at} ({acc_diff} ago)"
            join_diff = await time_diff(datetime.utcnow(), user.joined_at)
            join_date = f"{user.joined_at} ({join_diff} ago)"
            roles_str = ""
            user_roles = user.roles
            user_roles.reverse()
            for role in user_roles:
                if role.is_default():
                    continue
                elif role == self.roles.spacer_pings or role == self.roles.spacer_special:
                    continue
                else:
                    roles_str += role.mention
                    roles_str += ","
                    roles_str += " "
            roles_str = f"**{roles_str[:-2]}**"

            embed = discord.Embed(
                title=title,
                color=0x3b88c3,
                description="─────────────────"
            )
            embed.add_field(name="Full Discord Tag", value=f"{user.mention}  -  {user}", inline=False)
            embed.add_field(name="ID", value=user.id, inline=False)
            embed.add_field(name="Account Created At", value=account_creation, inline=False)
            embed.add_field(name="User Joined At", value=join_date, inline=False)
            embed.add_field(name="Roles", value=roles_str, inline=False)
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_footer(icon_url=self.user.avatar_url,
                             text="User info of {} - requested by {}".format(user, ctx.message.author))

            if ctx.channel.id == self.channels.docs.id or ctx.channel.id == self.channels.staff_bot.id:
                await ctx.send(embed=embed)
            else:
                docs_sent = self.basic_embed(True, "User Information **sent**!")
                await ctx.send(embed=docs_sent)
                await self.channels.docs.send(embed=embed, content=ctx.message.author.mention)
        else:
            embed = self.basic_embed(False, "User **not found**!")
            await ctx.send(embed=embed)

    async def send_docs(self, ctx: discord.ext.commands.Context, embed):
        if ctx.channel.id == self.channels.docs.id or ctx.channel.id == self.channels.staff_bot.id:
            await ctx.send(embed=embed)

        else:
            docs_sent = self.basic_embed(True, "Documentations **sent**!")
            msg = await ctx.send(embed=docs_sent)
            await self.channels.docs.send(embed=embed, content=ctx.author.mention)
            await msg.delete(delay=5)


if __name__ == "__main__":
    bot = Shiro()
