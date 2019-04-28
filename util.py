from discord import Embed
from datetime import datetime


async def time_diff(t1, t2):
    return strfdelta(t1 - t2).replace("s", "").replace(" hour", "h").replace(" day", "d").replace(" minute", "m")


def strfdelta(tdelta):
    t = {'days': 'days',
         'hours': 'hours',
         'minutes': 'minutes'
         }

    d = {'days': tdelta.days}
    d['hours'], rem = divmod(tdelta.seconds, 3600)
    d['minutes'], d['seconds'] = divmod(rem, 60)
    if d['days'] is 1:
        t['days'] = 'day'
    if d['hours'] is 1:
        t['hours'] = 'hour'
    if d['minutes'] is 1:
        t['minutes'] = 'minute'
    if d['seconds'] is 1:
        t['seconds'] = 'second'
    if d['days'] is 0:
        if d['hours'] is 0:
            return '{} {}'.format(d['minutes'] + 1, t['minutes'])
        return '{} {} {} {}'.format(d['hours'], t['hours'], d['minutes'] + 1, t['minutes'],)
    return '{} {} {} {} {} {}'.format(d['days'], t['days'], d['hours'], t['hours'], d['minutes'] + 1, t['minutes'])


def delta_clean_up(delta_string):
    new_string = ""
    for letter in delta_string:
        if not letter == " ":
            new_string += letter
        else:
            try:
                int(last_letter)
            except ValueError:
                new_string += ", "
            else:
                new_string += letter
        last_letter = letter

    return " and".join(new_string.rsplit(",", 1))


async def season_int_to_str(season_int):
    season_str = str(season_int).rjust(3, "0")
    year = int(season_str[:2])
    season = int(season_str[2:])

    if year > 60:
        year += 1900
    else:
        year += 2000

    if season == 1:
        season_str = "Winter"
    elif season == 2:
        season_str = "Spring"
    elif season == 3:
        season_str = "Summer"
    elif season == 4:
        season_str = "Fall"

    return f"{season_str} {year}"


async def build_embed(data):
    if not data:
        return None
    else:
        title_r = data["title"]["romaji"]
        title_e = data["title"]["english"]
        title_n = data["title"]["native"]
        aka_str = ""
        if title_e:
            aka_str += "**English**: {}".format(title_e)
        if title_e and title_n:
            aka_str += "\n"
        if title_n:
            aka_str += "**Native**: {}".format(title_n)
        aka_str += "\n** **"

        site_url = data["siteUrl"]
        desc = "\n─────────────────\n" + data["description"].split("<br>")[0].replace("<i>", "").replace("</i>", "")
        if len(desc) >= 261:
            desc = desc[:260].strip() + "... [read more]({})".format(site_url)
        cover_url = data["coverImage"]["extraLarge"]

        embed_color = data["coverImage"]["color"]
        if embed_color:
            embed_color = embed_color.replace("#", "")
        else:
            embed_color = "ffffff"

        studio = data["studios"]["edges"]
        if studio:
            try:
                studio = studio[0]["node"]["name"]
            except IndexError:
                studio = "TBA"
        else:
            studio = "TBA"

        tv_format = data["format"]

        season_int = data["seasonInt"]
        try:
            season_str = await season_int_to_str(season_int)
        except Exception:
            season_str = "--"

        status = str(data["status"]).capitalize()
        if status.lower() == "not_yet_released":
            status = "Not Yet Released"
        score = data["meanScore"]
        if not score:
            score = "--"
        avg_score = data["averageScore"]

        genres = data["genres"]
        genres_str = ""
        for genre in genres:
            genres_str += genre
            genres_str += ", "
        genres_str = genres_str.strip()[:-1]

        embed = Embed(
            title=f"**{title_r}**",
            url=site_url,
            description=desc,
            color=int(embed_color, 16)
        )

        embed.set_thumbnail(url=cover_url)
        embed.add_field(name="Also known as:", value=aka_str, inline=False)
        embed.add_field(name="Studio", value=f"{studio}")
        embed.add_field(name="Season", value=season_str)
        embed.add_field(name="Average Rating", value=f"{score}%")
        embed.add_field(name="Status", value=status)
        embed.add_field(name="Genres", value=genres_str, inline=False)

        return [embed, title_r]


async def build_manga_embed(data):
    if not data:
        return None
    else:
        title_r = data["title"]["romaji"]
        title_e = data["title"]["english"]
        title_n = data["title"]["native"]
        aka_str = ""
        if title_e:
            aka_str += "**English**: {}".format(title_e)
        if title_e and title_n:
            aka_str += "\n"
        if title_n:
            aka_str += "**Native**: {}".format(title_n)
        aka_str += "\n** **"

        site_url = data["siteUrl"]
        desc = "\n─────────────────\n" + data["description"].split("<br>")[0].replace("<i>", "").replace("</i>", "")
        if len(desc) >= 261:
            desc = desc[:260].strip() + "... [read more]({})".format(site_url)
        cover_url = data["coverImage"]["extraLarge"]

        embed_color = data["coverImage"]["color"]
        if embed_color:
            embed_color = embed_color.replace("#", "")
        else:
            embed_color = "ffffff"

        author_data = data["staff"]["nodes"][0]["name"]
        author = author_data["first"] + " " + author_data["last"]

        start_data = data["startDate"]
        start_month = start_data['month']
        if start_month == 1:
            month = 'Jan'
        elif start_month == 2:
            month = 'Feb'
        elif start_month == 3:
            month = 'Mar'
        elif start_month == 4:
            month = 'Apr'
        elif start_month == 5:
            month = 'May'
        elif start_month == 6:
            month = 'Jun'
        elif start_month == 7:
            month = 'Jul'
        elif start_month == 8:
            month = 'Aug'
        elif start_month == 9:
            month = 'Sept'
        elif start_month == 10:
            month = 'Oct'
        elif start_month == 11:
            month = 'Nov'
        elif start_month == 12:
            month = 'Dec'
        else:
            month = "Not Defined"

        if month == "Not Defined" and start_data['year']:
            start = start_data['year']
        elif not start_data['year']:
            start = 'TBD'
        else:
            start = f"{month} {start_data['day']}, {start_data['year']}"

        status = str(data["status"]).capitalize()
        if status.lower() == "not_yet_released":
            status = "Not Yet Released"

        score = data["meanScore"]

        if not score:
            score = "--"

        genres = data["genres"]
        genres_str = ""
        for genre in genres:
            genres_str += genre
            genres_str += ", "
        genres_str = genres_str.strip()[:-1]

        embed = Embed(
            title=f"**{title_r}**",
            url=site_url,
            description=desc,
            color=int(embed_color, 16)
        )

        embed.set_thumbnail(url=cover_url)
        embed.add_field(name="Also known as:", value=aka_str, inline=False)
        embed.add_field(name="Author", value=f"{author}")
        embed.add_field(name="Start Date", value=start)
        embed.add_field(name="Average Rating", value=f"{score}%")
        embed.add_field(name="Status", value=status)
        embed.add_field(name="Genres", value=genres_str, inline=False)

        return [embed, title_r]


async def build_small_embed(data):
    if not data:
        return None
    else:
        title_r = data["title"]["romaji"]
        title_e = data["title"]["english"]
        title_n = data["title"]["native"]
        aka_str = ""
        if title_e:
            aka_str += "**English**: {}".format(title_e)
        if title_e and title_n:
            aka_str += "\n"
        if title_n:
            aka_str += "**Native**: {}".format(title_n)
        aka_str += "\n** **"

        site_url = data["siteUrl"]
        cover_url = data["coverImage"]["extraLarge"]

        embed_color = data["coverImage"]["color"]
        if embed_color:
            embed_color = embed_color.replace("#", "")
        else:
            embed_color = "ffffff"

        status = str(data["status"]).capitalize()
        if status.lower() == "not_yet_released":
            status = "Not Yet Released"
        score = data["meanScore"]
        if not score:
            score = "--"
        avg_score = data["averageScore"]

        genres = data["genres"]
        genres_str = ""
        for genre in genres:
            genres_str += genre
            genres_str += ", "
        genres_str = genres_str.strip()[:-1]

        embed = Embed(
            title=f"**{title_r}**",
            url=site_url,
            description="\n─────────────────\n",
            color=int(embed_color, 16)
        )

        embed.set_thumbnail(url=cover_url)
        embed.add_field(name="Also known as:", value=aka_str, inline=False)
        embed.add_field(name="Average Rating", value=f"{score}%")
        embed.add_field(name="Status", value=status)
        embed.add_field(name="Genres", value=genres_str, inline=False)

        return [embed, title_r]


async def build_small_manga_embed(data):
    if not data:
        return None
    else:
        title_r = data["title"]["romaji"]
        title_e = data["title"]["english"]
        title_n = data["title"]["native"]
        aka_str = ""
        if title_e:
            aka_str += "**English**: {}".format(title_e)
        if title_e and title_n:
            aka_str += "\n"
        if title_n:
            aka_str += "**Native**: {}".format(title_n)
        aka_str += "\n** **"

        site_url = data["siteUrl"]
        cover_url = data["coverImage"]["extraLarge"]

        embed_color = data["coverImage"]["color"]
        if embed_color:
            embed_color = embed_color.replace("#", "")
        else:
            embed_color = "ffffff"

        status = str(data["status"]).capitalize()
        if status.lower() == "not_yet_released":
            status = "Not Yet Released"

        score = data["meanScore"]

        if not score:
            score = "--"

        genres = data["genres"]
        genres_str = ""
        for genre in genres:
            genres_str += genre
            genres_str += ", "
        genres_str = genres_str.strip()[:-1]

        embed = Embed(
            title=f"**{title_r}**",
            url=site_url,
            description="\n─────────────────\n",
            color=int(embed_color, 16)
        )

        embed.set_thumbnail(url=cover_url)
        embed.add_field(name="Also known as:", value=aka_str, inline=False)
        embed.add_field(name="Average Rating", value=f"{score}%")
        embed.add_field(name="Status", value=status)
        embed.add_field(name="Genres", value=genres_str, inline=False)

        return [embed, title_r]


async def build_next_ep_embed(data, epoch: int = None, episode: int = None):
    if epoch:
        airing_at = epoch
    else:
        schedule = data["airingSchedule"]["edges"][0]["node"]
        airing_at = schedule["airingAt"]
        episode = schedule["episode"]
    title = data["title"]["romaji"]
    site_url = data["siteUrl"]
    desc = "─────────────────\n" + data["description"].split("<br>")[0].replace("<i>", "").replace("</i>", "")
    if len(desc) >= 141:
        desc = desc[:140].strip() + "... [read more]({})".format(site_url)
    else:
        desc += (140 - len(desc)) * " "
        desc += "** **"
    next_ep = datetime.utcfromtimestamp(airing_at)
    time_until_next_ep = await time_diff(next_ep, datetime.utcnow())
    if "-" in time_until_next_ep or time_until_next_ep.lower() == "0m":
        return False

    embed = Embed(
        title=f"**{title}**",
        description=desc,
        url=site_url,
        color=0x89af5b,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=data["coverImage"]["extraLarge"])
    embed.add_field(name="** **", value=f":clock8: **Episode {episode}**: in __**{time_until_next_ep}**.__",
                    inline=False)

    return [embed, title]