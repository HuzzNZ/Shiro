import praw
import random
from discord import Embed
from praw import models
from datetime import datetime


class Reddit:
    def __init__(self, reddit_instance):
        self.reddit = reddit_instance
        self.submission = praw.models.Submission

    async def get_random_animeme(self):
        subreddit = self.reddit.subreddit("Animemes")
        top_submissions = []
        counter = 0
        for submission in subreddit.top("day"):
            top_submissions.append(submission)
            counter += 1
            if counter >= 15:
                break
        self.submission = random.choice(top_submissions)

    async def check_for_video(self):
        has_video = True
        while has_video:
            s_url = self.submission.url
            if "v.redd.it" in s_url:
                await self.get_random_animeme()
            else:
                has_video = False

    async def get_embed(self):
        s_title = self.submission.title
        s_url = self.submission.url
        s_subreddit = self.submission.subreddit
        s_author = self.submission.author
        s_author_icon = s_author.icon_img
        s_karma = self.submission.score
        s_created_epoch = self.submission.created_utc
        s_link = self.submission.permalink

        title = f":closed_book:  **{s_title}** on r/{s_subreddit}"
        desc = f"─────────────────\n:small_red_triangle:  **{s_karma}**\n:link:  " \
            f"**[Permalink](https://reddit.com{s_link})**"
        footer_text = f"By u/{s_author}"

        embed = Embed(
            title=title,
            description=desc,
            timestamp=datetime.utcfromtimestamp(s_created_epoch),
            color=0xdd2e44
        )
        embed.set_footer(text=footer_text, icon_url=s_author_icon)
        embed.set_image(url=s_url)

        return embed
