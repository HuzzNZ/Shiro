from discord import Embed


# subcommand = {
#     "name": "Adding your waifu",
#
#     "usages": [
#         "!mywaifu is <name>",
#         "!mywaifu add <name>"
#     ],
#
#     "function": "Adds a Special Role under your roles of a waifu you specified. Max 24 Chars."
# }


class Command:
    def __init__(self, command, subcommands: list):
        self.command = command
        self.subcommands = subcommands

        self.embed_fields = []
        self.to_embed_field()

    def to_embed_field(self):
        return_list = []
        for sc in self.subcommands:
            name = sc["name"]

            usage_str = ""
            for usage in sc['usages']:
                usage_str += f" `{usage}` /"
            usage_str = ":black_small_square: " + usage_str.strip()[:-2]

            function = sc['function']

            value = f"{usage_str}\n{function}"
            return_list.append({"name": name, "value": value})

        self.embed_fields = return_list


class Docs:
    def __init__(self):
        self.anime = None
        self.anime_embed()

        self.manga = None
        self.manga_embed()

        self.nextep = None
        self.nextep_embed()

        self.waifu = None
        self.waifu_embed()

        self.dice = None
        self.dice_embed()

        self.cointoss = None
        self.cointoss_embed()

        self.eightball = None
        self.eightball_embed()

        self.members = None
        self.members_embed()

        self.mywaifu = None
        self.mywaifu_embed()

        self.userinfo_whois = None
        self.userinfo_whois_embed()

        self.idol = None
        self.idol_embed()

        self.list_cmds = [
            "anime", "manga", "nextep", "waifu", "dice", "cointoss", "8ball", "members", "mywaifu", "userinfo", "whois",
            "idol"
        ]

    def build_embed(self, cmd: Command):
        if cmd.command == "eightball":
            command = "8ball"
        else:
            command = cmd.command
        embed = Embed(
            title=":information_source:   **!{}** Documentation Panel".format(command),
            description="─────────────────────────",
            color=0x3b88c3
        )

        for embed_field in cmd.embed_fields:
            embed.add_field(name=embed_field["name"], value=f"{embed_field['value']}\n──────", inline=False)

        return embed

    def anime_embed(self):
        subcommands = [
            {
                "name": "Searching Anime by ID",

                "usages": [
                    "!anime <anilist id>"
                ],

                "function": "Searches for an Anime Title on the anilist.co API using the given ID, and returns "
                            "information if found."
            },
            {
                "name": "Searching Anime by Name",

                "usages": [
                    "!anime <name>"
                ],

                "function": "Searches for an Anime Title on the anilist.co API using the given name, and returns "
                            "the first title's information (if found)."
            },
        ]

        cmd = Command("anime", subcommands)
        self.anime = self.build_embed(cmd)

    def manga_embed(self):
        subcommands = [
            {
                "name": "Searching Manga by ID",

                "usages": [
                    "!anime <anilist id>"
                ],

                "function": "Searches for a Manga Title on the anilist.co API using the given ID, and returns "
                            "information if found."
            },
            {
                "name": "Searching Manga by Name",

                "usages": [
                    "!anime <name>"
                ],

                "function": "Searches for a Manga Title on the anilist.co API using the given name, and returns the "
                            "first title's information (if found)."
            },
        ]

        cmd = Command("manga", subcommands)
        self.manga = self.build_embed(cmd)

    def nextep_embed(self):
        subcommands = [
            {
                "name": "Fetching the Next Episode's Airing Time by ID",

                "usages": [
                    "!nextep <anilist id>"
                ],

                "function": "Searches for an Anime Title on the anilist.co API using the given ID, and if the anime is "
                            "currently airing, returns the relative airing time for the next episode of said title."
            },
            {
                "name": "Fetching the Next Episode's Airing Time by Name",

                "usages": [
                    "!nextep <name>"
                ],

                "function": "Searches for an Anime Title on the anilist.co API using the given name, and if the anime "
                            "is currently airing, returns the relative airing time for the next episode of said title."
            }
        ]

        cmd = Command("nextep", subcommands)
        self.nextep = self.build_embed(cmd)

    def waifu_embed(self):
        subcommands = [
            {
                "name": "Randomly Generate a waifu",

                "usages": [
                    "!waifu"
                ],

                "function": "Randomly Generates a waifu from Gwern Branwen's StyleGAN Neural Network."
            },
            {
                "name": "Recall a waifu by ID",

                "usages": [
                    "!waifu [id]"
                ],

                "function": "Finds a specific waifu image from Gwern Branwen's StyleGAN Neural Network database by its"
                            " unique ID. (Up to 99,999)"
            },
        ]

        cmd = Command("waifu", subcommands)
        self.waifu = self.build_embed(cmd)

    def dice_embed(self):
        subcommands = [
            {
                "name": "Roll a 6-sided dice",

                "usages": [
                    "!dice"
                ],

                "function": "Just.. rolls a 6 sided dice once."
            },
            {
                "name": "Roll an x-sided dice",

                "usages": [
                    "!dice [x]"
                ],

                "function": "Rolls a dice with an [x] amount of sides once. Maximum 1,000,000,000, Minimum 1."
            },
        ]

        cmd = Command("dice", subcommands)
        self.dice = self.build_embed(cmd)

    def cointoss_embed(self):
        subcommands = [
            {
                "name": "Tosses a coin",

                "usages": [
                    "!cointoss"
                ],

                "function": "Returns either Heads or Tails."
            },
        ]

        cmd = Command("cointoss", subcommands)
        self.cointoss = self.build_embed(cmd)

    def eightball_embed(self):
        subcommands = [
            {
                "name": "Ask the Magic 8-ball a question",

                "usages": [
                    "!8ball <question>"
                ],

                "function": "The Magic 8-ball returns an answer given the question."
            },
        ]

        cmd = Command("eightball", subcommands)
        self.eightball = self.build_embed(cmd)

    def members_embed(self):
        subcommands = [
            {
                "name": "Amount of members",

                "usages": [
                    "!members"
                ],

                "function": "Returns the number of Members + Bots currently in this server."
            },
        ]

        cmd = Command("members", subcommands)
        self.members = self.build_embed(cmd)

    def mywaifu_embed(self):
        subcommands = [
            {
                 "name": "Adding your waifu",

                 "usages": [
                     "!mywaifu is <name>",
                     "!mywaifu add <name>"
                 ],

                 "function": "Adds a Special Role under your roles of a waifu you specified. Max 24 Chars."
            },
            {
                 "name": "Changing your waifu",

                 "usages": [
                     "!mywaifu isnow <name>",
                     "!mywaifu change <name>"
                 ],

                 "function": "Removes your current waifu and changes it to the waifu you specified. Max 24 Chars."
            },
            {
                 "name": "Removing your waifu",

                 "usages": [
                     "!mywaifu delete",
                     "!mywaifu isnolonger"
                 ],

                 "function": "Removes your current waifu."
            }
        ]

        cmd = Command("mywaifu", subcommands)
        self.mywaifu = self.build_embed(cmd)

    def userinfo_whois_embed(self):
        subcommands = [
            {
                "name": "Your own user information",

                "usages": [
                    "!whois",
                    "!userinfo"
                ],

                "function": "Returns your user information. If not used inside <#557033330470813697>, the bot will"
                            "ping the command caller inside that channel and send the information there. Aliased to"
                            "`!whois` and `!userinfo`. This applies to all subcommands under this command tree."
            },
            {
                "name": "Another user's information",

                "usages": [
                    "!whois [user name]",
                    "!whois [user id]",
                    "!whois [user @mention]"
                ],

                "function": "Returns a specific user's information if found."
            },
        ]

        cmd = Command("whois / !userinfo", subcommands)
        self.userinfo_whois = self.build_embed(cmd)

    def idol_embed(self):
        subcommands = [
            {
                "name": "Random Love Live! Idol card by Name",

                "usages": [
                    "!idol <Idol Name>"
                ],

                "function": "Returns an embed with a random Love Live! School Idol Festival Card to be displayed. Only "
                            "Members of Aqours, μ's and A-RISE are avaliable. (Might take a long time)"
            },
            {
                "name": "Random Love Live! Idol card by School",

                "usages": [
                    "!idol <School Name>"
                ],

                "function": "Functions similarly to name command. Only Otonokizaka, and Uranohoshi are avaliable as"
                            "options. (Will take a long time)"
            },
            {
                "name": "Random Love Live! Idol card by Group",

                "usages": [
                    "!idol <Group Name>"
                ],

                "function": "Functions similarly to name command. Very Similar to school command. Only Aqours, and μ's "
                            "are avaliable as options. (Will take a long time)"
            },
        ]

        cmd = Command("idol", subcommands)
        self.idol = self.build_embed(cmd)


if __name__ == "__main__":
    docs = Docs()
