from discord import Embed

import requests
import json
import os


class Osu:
    def __init__(self, api_key):
        self.api = api_key

        self.url_base = "https://osu.ppy.sh/api/"
        self.avatar_url_base = "https://a.ppy.sh/"
        self.username = None

        self.base_path = os.path.abspath("osu_api.py")
        if "shiro/apis" in self.base_path:
            in_folder = ""
        else:
            in_folder = "shiro"
        self.associations_file = self.base_path.replace("osu_api.py", os.path.join(in_folder, "osu.json"))

        self.associations = {}
        self.load_associations()

    def write_association(self, association_dict):
        with open(self.associations_file, "w", encoding="UTF-8") as file:
            json.dump(association_dict, file)

    def load_associations(self):
        with open(self.associations_file, "r", encoding="UTF-8") as file:
            content = json.loads(file.read())
        self.associations = content
        return content

    def find_user(self, user_id):
        self.load_associations()
        self.find_user_after_load(user_id)

    def find_user_after_load(self, user_id):
        try:
            self.username = self.associations[(str(user_id))]
        except KeyError:
            self.username = None
            embed = Embed(
                title=":warning:  **Hey, you don't seem to have an osu! account associated!**",
                color=0xffcc1b,
            )
            embed.set_footer(text="You can use `!osu set <osu! username>` to associate yourself with one.")
            return embed

    async def set_user(self, user_id, osu_username):
        self.load_associations()
        x = await self.set_user_after_load(user_id, osu_username)
        return x

    async def set_user_after_load(self, user_id, osu_username):
        params = {
            "k": self.api,
            "u": osu_username,
            "type": "string"}

        r = requests.get(url=self.url_base + "get_user", params=params).text
        try:
            response = json.loads(r)[0]
        except IndexError:
            embed = Embed(
                title=":no_entry:  **osu! Account not found!**",
                color=0x89af5b,
                description="─────────────────\nPlease re-check and make sure that you have the correct capitalization,"
                            " spelling and spacing of your username."
            )
            embed.set_thumbnail(url="https://a.ppy.sh/01.png")
            return embed

        u_id = response["user_id"]
        u_name = response["username"]
        u_avatar_url = self.url_base + u_id + ".png"

        associations_dict = self.load_associations()
        associations_dict[str(user_id)] = u_id
        self.write_association(associations_dict)

        embed = Embed(
            title=":white_check_mark:  **osu! Association set!**",
            color=0x89af5b,
            description="─────────────────\n**Username:** {}\n **User ID**: {}".format(u_name, u_id)
        )
        embed.set_thumbnail(url=u_avatar_url)
        return embed
