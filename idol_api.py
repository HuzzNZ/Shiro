import requests
import asyncio
import random
import math

from discord import Embed


class Idol:
    def __init__(self):
        self.name = None
        self.card_id = None
        self.school = None
        self.year = None
        self.unit = None
        self.results = None
        self.discordEmbed = None

    def set_name(self, i_name: str):
        i_name = i_name.lower()
        f_name = None
        uranohoshi = {
            "chika": "Takami Chika",
            "riko": "Sakurauchi Riko",
            "kanan": "Matsuura Kanan",
            "dia": "Kurosawa Dia",
            "you": "Watanabe You",
            "yoshiko": "Tsushima Yoshiko",
            "hanamaru": "Kunikida Hanamaru",
            "mari": "Ohara Mari",
            "ruby": "Kurosawa Ruby"
        }
        otonokizaka = {
            "honoka": "Kousaka Honoka",
            "eli": "Ayase Eli",
            "kotori": "Minami Kotori",
            "umi": "Sonoda Umi",
            "rin": "Hoshizora Rin",
            "maki": "Nishikino Maki",
            "nozomi": "Toujou Nozomi",
            "hanayo": "Koizumi Hanayo",
            "nico": "Yazawa Nico"
        }
        arise = {
            "tsubasa": "Kira Tsubasa",
            "anju": "Yuuki Anju",
            "erena": "Toudou Erena"
        }
        name_dict = {
            "chika": uranohoshi["chika"],
            "takami": uranohoshi["chika"],
            "chika takami": uranohoshi["chika"],
            "takami chika": uranohoshi["chika"],

            "riko": uranohoshi["riko"],
            "sakurauchi": uranohoshi["riko"],
            "riko sakurauchi": uranohoshi["riko"],
            "riko sakurachi": uranohoshi["riko"],
            "sakurauchi riko": uranohoshi["riko"],
            "sakurachi riko": uranohoshi["riko"],

            "kanan": uranohoshi["kanan"],
            "matsuura": uranohoshi["kanan"],
            "kanan matsuura": uranohoshi["kanan"],
            "kanan matsura": uranohoshi["kanan"],
            "matsuura kanan": uranohoshi["kanan"],
            "matsura kanan": uranohoshi["kanan"],

            "dia": uranohoshi["dia"],
            "dia kurosawa": uranohoshi["dia"],
            "kurosawa dia": uranohoshi["dia"],

            "you": uranohoshi["you"],
            "yousoro": uranohoshi["you"],
            "watanabe": uranohoshi["you"],
            "you watanabe": uranohoshi["you"],
            "watanabe you": uranohoshi["you"],

            "yoshiko": uranohoshi["yoshiko"],
            "yohane": uranohoshi["yoshiko"],
            "tsushima": uranohoshi["yoshiko"],
            "yoshiko tsushima": uranohoshi["yoshiko"],
            "yohane tsushima": uranohoshi["yoshiko"],
            "tsushima yoshiko": uranohoshi["yoshiko"],
            "tsushima yohane": uranohoshi["yoshiko"],

            "hanamaru": uranohoshi["hanamaru"],
            "kunikida": uranohoshi["hanamaru"],
            "hanamaru kunikida": uranohoshi["hanamaru"],
            "kunikida hanamaru": uranohoshi["hanamaru"],

            "mari": uranohoshi["mari"],
            "ohara": uranohoshi["mari"],
            "mari ohara": uranohoshi["mari"],
            "ohara mari": uranohoshi["mari"],

            "ruby": uranohoshi["ruby"],
            "ruby kurosawa": uranohoshi["ruby"],
            "kurosawa ruby": uranohoshi["ruby"],

            "honoka": otonokizaka["honoka"],
            "kousaka": otonokizaka["honoka"],
            "kosaka": otonokizaka["honoka"],
            "kōsaka": otonokizaka["honoka"],
            "honoka kousaka": otonokizaka["honoka"],
            "honoka kosaka": otonokizaka["honoka"],
            "honoka kōsaka": otonokizaka["honoka"],
            "kousaka honoka": otonokizaka["honoka"],
            "kosaka honoka": otonokizaka["honoka"],
            "kōsaka honoka": otonokizaka["honoka"],

            "eli": otonokizaka["eli"],
            "eli-chi": otonokizaka["eli"],
            "ayase": otonokizaka["eli"],
            "eli ayase": otonokizaka["eli"],
            "ayase eli": otonokizaka["eli"],

            "kotori": otonokizaka["kotori"],
            "minami": otonokizaka["kotori"],
            "kotori minami": otonokizaka["kotori"],
            "minami kotori": otonokizaka["kotori"],

            "umi": otonokizaka["umi"],
            "sonoda": otonokizaka["umi"],
            "umi sonoda": otonokizaka["umi"],
            "sonoda umi": otonokizaka["umi"],

            "rin": otonokizaka["rin"],
            "hoshizora": otonokizaka["rin"],
            "rin hoshizora": otonokizaka["rin"],
            "hoshizora rin": otonokizaka["rin"],

            "maki": otonokizaka["maki"],
            "nishikino": otonokizaka["maki"],
            "maki nishikino": otonokizaka["maki"],
            "nishikino maki": otonokizaka["maki"],

            "nozomi": otonokizaka["nozomi"],
            "toujou": otonokizaka["nozomi"],
            "tojo": otonokizaka["nozomi"],
            "tōjō": otonokizaka["nozomi"],
            "nozomi toujou": otonokizaka["nozomi"],
            "nozomi tojo": otonokizaka["nozomi"],
            "nozomi tōjō": otonokizaka["nozomi"],
            "toujou nozomi": otonokizaka["nozomi"],
            "tojo nozomi": otonokizaka["nozomi"],
            "tōjō nozomi": otonokizaka["nozomi"],

            "hanayo": otonokizaka["hanayo"],
            "koizumi": otonokizaka["hanayo"],
            "hanayo koizumi": otonokizaka["hanayo"],
            "koizumi hanayo": otonokizaka["hanayo"],

            "nico": otonokizaka["nico"],
            "yazawa": otonokizaka["nico"],
            "nico yazawa": otonokizaka["nico"],
            "yazawa nico": otonokizaka["nico"],

            "tsubasa": arise["tsubasa"],
            "kira": arise["tsubasa"],
            "tsubasa kira": arise["tsubasa"],
            "kira tsubasa": arise["tsubasa"],

            "anju": arise["anju"],
            "yuuki": arise["anju"],
            "yuki": arise["anju"],
            "anju yuuki": arise["anju"],
            "anju yuki": arise["anju"],
            "yuuki anju": arise["anju"],
            "yuki anju": arise["anju"],

            "erena": arise["erena"],
            "toudou": arise["erena"],
            "todo": arise["erena"],
            "tōdō": arise["erena"],
            "erena toudou": arise["erena"],
            "erena todo": arise["erena"],
            "erena tōdō": arise["erena"],
            "toudou erena": arise["erena"],
            "todo erena": arise["erena"],
            "tōdō erena": arise["erena"],
        }
        try:
            f_name = name_dict[i_name]
        except KeyError:
            i_name_l = i_name.split(" ")
            found = False
            for part in i_name_l:
                if not found:
                    try:
                        f_name = name_dict[part]
                        found = True
                    except KeyError:
                        continue
                else:
                    break
        if not f_name:
            raise IdolSearchError("Name Not Found")
        else:
            self.name = f_name

    def set_id(self, card_id):
        try:
            card_id = int(card_id)
        except:
            raise IdolSearchError("ID Not Int")
        self.card_id = card_id

    def set_school(self, school: str):
        school = school.lower()
        if school == "u" or school == "urano" or school == "uranohoshi" or "urano" in school:
            self.school = "Uranohoshi Girls' High School"
        elif school == "o" or school == "otono" or school == "otonokizaka" or "otono" in school:
            self.school = "Otonokizaka Academy"
        else:
            raise IdolSearchError("School Not Found")

    def set_year(self, year):
        try:
            year = int(year)
        except ValueError:
            raise IdolSearchError("Year Not Int")
        if year == 1:
            self.year = "First"
        elif year == 2:
            self.year = "Second"
        elif year == 3:
            self.year = "Third"
        else:
            raise IdolSearchError("Year Not Between 1-3")

    def set_unit(self, unit: str):
        unit = unit.lower()
        units = {
            "u": "μ's",
            "a": "Aqours"
        }
        aliases = {
            "muse": units["u"],
            "u's": units["u"],
            "us": units["u"],
            "u": units["u"],
            "μ's": units["u"],
            "μs": units["u"],
            "μ": units["u"],

            "aqours": units["a"],
            "aqour": units["a"],
            "aq": units["a"],
            "a": units["a"],
        }
        try:
            f_unit = aliases[unit]
        except KeyError:
            raise IdolSearchError("Unit Not Found")
        self.unit = f_unit

    def set(self, arg):
        try:
            self.set_name(arg)
            return
        except IdolSearchError:
            try:
                self.set_unit(arg)
                return
            except IdolSearchError:
                try:
                    self.set_school(arg)
                    return
                except IdolSearchError:
                    try:
                        self.set_year(arg)
                        return
                    except:
                        raise AttributeError("None of this matches anything wtf")

    async def retrieve(self, l_id: int = None):
        params = {
            "page_size": 100
        }
        if self.name:
            params["name"] = self.name
        elif self.unit:
            params["idol_main_unit"] = self.unit
        elif self.school:
            params["idol_school"] = self.school
        elif self.year:
            params["idol_year"] = self.year
        else:
            if l_id:
                params["ids"] = l_id
            else:
                return None

        run_loop = True
        loop_iterations = None
        starting_dict = requests.get("http://schoolido.lu/api/cards/", params=params).json()

        if starting_dict["count"] < params["page_size"]:
            run_loop = False
        else:
            loop_iterations = math.ceil(starting_dict["count"] / params["page_size"])

        results = starting_dict["results"]

        if run_loop:
            next_url = starting_dict["next"]
            for i in range(1, loop_iterations):
                r_dict = requests.get(next_url).json()
                next_url = r_dict["next"]
                results += r_dict["results"]

        self.results = results

    async def random_embed(self):
        card = random.choice(self.results)
        card_url = card["card_image"]
        while not card_url:
            card = random.choice(self.results)
            card_url = card["card_image"]

        embed_color = 0x55acee
        name_en = card["idol"]["name"]
        name_ja = card["idol"]["japanese_name"].replace("　", "")
        unit = card["idol"]["main_unit"]
        school = card["idol"]["school"].split(" ")[0] + " - " + card["idol"]["year"] + " Year"

        footer_url = "http:" + card["round_card_image"]
        footer_text = f"{name_en} - Card ID {card['id']}"
        card_url = "http:" + card_url

        embed = Embed(
            color=embed_color,
            title=":microphone:  **{}** - {}".format(name_en, unit),
            description=f"─────────────────\n{name_en} ({name_ja})\n**{unit}**@{school}"
        )
        embed.set_footer(icon_url=footer_url, text=footer_text)
        embed.set_image(url=card_url)
        return embed

    async def get_random_embed(self, arg):
        self.set(arg)
        await self.retrieve()
        embed_return = await self.random_embed()
        return embed_return


class IdolSearchError(Exception):
    def __init__(self, error=None):
        super().__init__(error)
        print(error)


if __name__ == "__main__":
    idol = Idol()
    idol.set("ruby")
    results = asyncio.get_event_loop().run_until_complete(idol.retrieve())
    card_url = random.choice(results)["card_image"]
    while not card_url:
        card_url = random.choice(results)["card_image"]
    print("http:" + card_url)
    #
    # print(random.choice(results))

    # params = {
    #     "idol_main_unit": "Aqours",
    #     "page_size": 100
    # }
    # print(requests.get("http://schoolido.lu/api/cards/", params=params).json())

    # params = {
    #     "idol_main_unit": "A-RISE",
    #     "page_size": 1000
    # }
    # return_dict = requests.get("http://schoolido.lu/api/cards/", params=params).json()
    # already_added = []
    # to_display = []
    # for i in return_dict["results"]:
    #     the_name = i["idol"]["name"]
    #     for name in already_added:
    #         if the_name == name:
    #             continue
    #     already_added.append(the_name)
    #     to_display.append(i)
    # for i in to_display:
    #     print(i["idol"]["name"])
