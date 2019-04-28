import discord
from discord.ext import commands
from discord.utils import get

from datetime import datetime

import asyncio

import signal

import sys

from anilist_api import find_anime_by_id
from anilist_api import find_manga_by_id
from anilist_api import find_anime_by_name
from anilist_api import find_manga_by_name

from util import build_next_ep_embed
from util import time_diff

from collections import namedtuple
import json
import os

from docs import Docs


class Shiro(commands.Bot):
    def __init__(self):
        # Inheriting discord.Client class
        super().__init__(command_prefix="!")

        # Finding bot platform
        self.on_windows = sys.platform == "win32"

        # Finding bot script base directory
        self.base_path = os.path.abspath("bot.py")

        # Finding File Directories
        if self.on_windows or "Shiro" in self.base_path:
            in_folder = ""
        else:
            in_folder = "Shiro"

        self.const_file = self.base_path.replace("bot.py", os.path.join(in_folder, "constants.json"))
        self.track_file = self.base_path.replace("bot.py", os.path.join(in_folder, "tracking.json"))
        self.track_msg_file = self.base_path.replace("bot.py", os.path.join(in_folder, "tracking_msg.json"))

        # Finding Client Token
        self.cred_file = self.base_path.replace("bot.py", os.path.join(in_folder, ".creds.json"))
        self.token = self.load_file(self.cred_file)["token"]

        # Making room for custom help command
        self.remove_command("help")

        # Loading Docs
        self.docs = Docs()

        # Loading Constants
        self.constants = self.load_file(self.const_file)
        self.senko_guild = namedtuple("Guild", "members")
        self.channel_ids = dict
        self.channels = namedtuple("Channel", "roles release uptime logs pins")
        self.role_ids = dict
        self.roles = namedtuple("Role", "kitsune member spacer_pings spacer_special "
                                        "news_server news_anime disc_anime disc_manga")

        # Loading Pin Threshold
        self.pin_threshold = self.constants["pin_threshold"]

        # Loading Tracking Messages
        self.tracking = self.load_file(self.track_file)
        self.tracking_msgs = self.load_file(self.track_msg_file)

        # Starting the bot
        self.send_log("Bot Client", "Starting process")

        if not sys.platform == "win32":
            self.loop.add_signal_handler(signal.SIGINT, lambda: self.loop.stop())
            self.loop.add_signal_handler(signal.SIGTERM, lambda: self.loop.stop())

        self.start_time = datetime.utcnow()
        self.loop.run_until_complete(self.login(token=self.token))
        self.loop.run_until_complete(self.connect(reconnect=True))

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
        return input_str.replace("<", "").replace("@", "").replace("!", "").replace(">", "")

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

    async def define_constants(self):
        self.senko_guild = self.get_guild(int(self.constants['guild']))

        # Loading Channels
        self.channel_ids = self.constants["channels"]
        Channel = namedtuple("Channel", "roles release uptime logs pins")

        roles = self.get_channel(id=int(self.channel_ids["roles"]))
        release = self.get_channel(id=int(self.channel_ids["release"]))
        uptime = self.get_channel(id=int(self.channel_ids["uptime"]))
        logs = self.get_channel(id=int(self.channel_ids["logs"]))
        pins = self.get_channel(id=int(self.channel_ids["pins"]))

        self.channels = Channel(roles, release, uptime, logs, pins)

        # Loading Roles

        self.role_ids = self.constants["roles"]
        Role = namedtuple("Role", "kitsune member spacer_pings spacer_special "
                                  "news_server news_anime disc_anime disc_manga")

        kitsune = get(self.senko_guild.roles, id=self.role_ids["kitsune"])
        member = get(self.senko_guild.roles, id=self.role_ids["member"])
        spacer_pings = get(self.senko_guild.roles, id=self.role_ids["spacer-pings"])
        spacer_special = get(self.senko_guild.roles, id=self.role_ids["spacer-special"])
        news_server = get(self.senko_guild.roles, id=self.role_ids["news-server"])
        news_anime = get(self.senko_guild.roles, id=self.role_ids["news-anime"])
        disc_anime = get(self.senko_guild.roles, id=self.role_ids["disc-anime"])
        disc_manga = get(self.senko_guild.roles, id=self.role_ids["disc-manga"])

        self.roles = Role(kitsune, member, spacer_pings, spacer_special, news_server, news_anime, disc_anime,
                          disc_manga)

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
            color=0x89af5b,
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
                await member.add_roles(member, self.roles.spacer_special)
                await member.add_roles(member, self.roles.spacer_pings)
                await member.add_roles(member, self.roles.member)

    async def refresh_presence(self):
        currently_playing = discord.Game(name=f"{'with {} users!'.format(len(self.senko_guild.members))}  ·  !help")
        await self.change_presence(activity=currently_playing)

    async def on_time_loop(self):
        hours = 0
        counter = 0
        ticks = 0
        await self.wait_until_ready()
        await self.define_constants()
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
                counter += 1
                ticks += 1
                await asyncio.sleep(0.5)
                if counter % 30 == 0:
                    self.loop.run_until_complete(self.refresh())
                if counter % 90 == 0:
                    self.loop.run_until_complete(self.refresh_24h())
                    self.loop.run_until_complete(self.refresh_presence())
                if ticks % 100 == 0:
                    await self.channels.uptime.send(f":large_blue_circle: I have been up for **{ticks}** ticks.")
                    self.loop.run_until_complete(self.refresh_roles())
                if counter == 7200:
                    hours += 1
                    await self.channels.uptime.send(f":large_blue_circle: **!!** I have been up for **{hours}** hours.")
                    self.send_log("Uptime", "The bot has been up for {} hours!".format(hours))
                    counter = 0
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
        self.send_log("Bot Client", "Ready on Discord")
        self.loop.create_task(self.on_time_loop())

    async def on_disconnect(self):
        self.send_log("Bot Client", "Disconnected")

    async def on_message(self, message):
        print(message.content)
        await self.process_commands(message)

    # ======================== #
    #                          #
    # ####### BOT CMDS ####### #
    #                          #
    # ======================== #

    async def ping(self, ctx):
        await ctx.send(content="Ping!")


bot = Shiro()
