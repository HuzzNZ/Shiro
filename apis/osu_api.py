from discord import Embed

import requests
import json
import os


class OsuAPI:
    def __init__(self, api_key):
        """
        Initializes the Osu API class.

        :param api_key: The API Key to use for the osu api.
        """
        self.api = api_key

        # Defining URL Bases
        self.url_base = "https://osu.ppy.sh/api/"
        self.avatar_url_base = "https://a.ppy.sh/"

        # Setting the paths for the associations json file
        self.base_path = os.path.abspath("osu_api_old.py")
        if "Shiro\\apis" in self.base_path:
            in_folder = ".."
        else:
            in_folder = "shiro"

        self.associations_file = self.base_path.replace("osu_api_old.py", os.path.join(in_folder, "osu.json"))

        self.mods_enum = [
            "NMD", "NF", "EZ", "TD", "HD", "HR", "SD", "DT", "RX", "HT", "NC", "FL", "CM", "SO", "AP", "PF"
        ]

    @staticmethod
    def build_user_not_found_embed():
        """
        Static Classmethod that returns a User Not Found Embed.

        :return: discord.Embed object
        """
        embed = Embed(
            title=":warning:  **Hey, you don't seem to have an osu! account associated!**",
            color=0xffcc1b,
        )
        embed.set_footer(text="You can use `!osu set <osu! username>` to associate yourself with one.")
        return embed

    def build_user_set_embed(self, user_data):
        """
        Builds an "Association set!" discord.Embed from a user data dict.

        :param user_data: The User Data dict, formatted the same as the osu API returns from /get_user
        :return: an Embed
        """
        user_id = user_data["user_id"]
        user_name = user_data["username"]
        user_avatar_url = self.avatar_url_base + user_id

        embed = Embed(
            title=":white_check_mark:  **osu! Association set!**",
            color=0x89af5b,
            description="─────────────────\n**osu! Username:** {}\n **osu! User ID**: {}".format(user_name, user_id)
        )
        embed.set_thumbnail(url=user_avatar_url)
        return embed

    def build_user_invalid_embed(self):
        """
        Builds an embed for when an osu account cannot be found with a specified osu! ID or username.

        :return: discord.Embed object
        """
        embed = Embed(
            title=":no_entry:  **osu! Account not found!**",
            color=0xa22c34,
            description="─────────────────\nPlease re-check and make sure that you have the correct capitalization,"
                        " spelling and spacing of your username."
        )
        embed.set_thumbnail(url=self.avatar_url_base + "01")
        return embed

    def bitwise_mods_to_str(self, bitwise_flag):
        """
        Converts osu bitwise enum mods to String Representation.

        :param bitwise_flag: A 16-bit bitwise flag for mods. Should be Int
        :return: The String Representation of the bitwise flag.
        """
        binary_flag = "{0:016b}".format(int(bitwise_flag))
        mods_list = []
        mods = ""

        for i in range(0, 16):
            if binary_flag[i] == 0:
                continue
            else:
                mods_list.append(i)

        if not mods_list:
            return "No Mod"
        else:
            for mod in mods_list:
                mods += self.mods_enum[mod]

        if "NC" in mods:
            mods = mods.replace("DT", "")
        if "PF" in mods:
            mods = mods.replace("SD", "")
        return mods

    def find_association(self, discord_user_id):
        """
        Finds an osu user association associated with a specified Discord ID.

        :param discord_user_id: The 18-digit Discord Snowflake ID
        :return: String osu ID, or an User Not Found Embed (discord.Embed object)
        """
        with open(self.associations_file, "r", encoding="UTF-8") as file:
            content = json.loads(file.read())
        try:
            osu_id = content[str(discord_user_id)]
            if osu_id:
                return osu_id
            else:
                return self.build_user_not_found_embed()
        except KeyError:  # If no associations found, return UNF Embed
            return self.build_user_not_found_embed()

    def create_association(self, discord_user_id,  osu_user):
        """
        Creates an association between a specified discord ID and an osu user ID (from the osu username).

        :param discord_user_id: The 18-digit Discord Snowflake ID
        :param osu_user: String osu Username / ID (auto detection)
        :return: An "Association Set!" discord.Embed if successful, False if osu ID not found
        """
        params = {
            "k": self.api,
            "u": osu_user
        }

        response = requests.get(url=self.url_base + "get_user", params=params).text
        response_json = json.loads(response)
        try:
            user = response_json[0]
        except IndexError:
            return False

        if user:
            with open(self.associations_file, "r+", encoding="UTF-8") as file:
                content = json.loads(file.read())
                content[str(discord_user_id)] = user["user_id"]
                json.dump(content, file)
            return self.build_user_set_embed(user)

    async def get_user_top5(self, osu_id):
        url = "get_user_best"
        params = {
            "k": self.api,
            "u": osu_id,
            "type": "id",
            "limit": 5
        }
        response = requests.get(url=self.url_base + url, params=params)
        data = json.loads(response)

        params_u = {
            "k": self.api,
            "u": osu_id,
            "type": "id"
        }
        response_u = requests.get(url=self.url_base + "get_user", params=params_u)
        data_u = json.loads(response_u)

        username = data_u["username"]
        for score in data:
            beatmap = await self.get_raw_beatmap_difficulty_data(osu_id)
            song_name = beatmap["title"]
            song_diff = beatmap["version"]
            song_star = beatmap["difficultyrating"]
            song_combo = beatmap["max_combo"]
            diff_mods = self.bitwise_mods_to_str(score["enabled_mods"])
            diff_score = score["score"]
            diff_combo = score["maxcombo"]
            acc_distrib = "[{}/{}/{}/{}]".format(
                score["count300"], score["count100"], score["count50"], score["countmiss"])



    async def get_user_recent(self, osu_id):
        pass

    async def get_user_profile(self, osu_id):
        pass

    async def get_raw_beatmap_difficulty_data(self, beatmap_id):
        """
        Returns raw data of a specific beatmap difficulty.

        :param beatmap_id: String beatmap_id of a specified difficulty.
        :return: Raw Data of the specified beatmap difficulty.
        """
        url = "get_beatmaps"
        params = {
            "k": self.api,
            "b": beatmap_id
        }
        response = requests.get(url=self.url_base + url, params=params).text
        return json.loads(response)[0]


osu = OsuAPI("abcd")
