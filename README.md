# Shiro - a discord.py bot

Shiro#3702 is a multifunctional discord bot that is rich in Anime / Manga functions, with general moderation and fun commands. This bot was built for the sole purpose to serve the Discord Server Ore no Senko-san, and has many features that is useful, interactive, and considers the general usage heuristics.

To try out the bot for yourself, you can join the Ore no Senko-san! server using [this link](https://discord.gg/VbKdA2y).

## Using this bot for yourself

As most of the constants are hard coded due to this bot being built for one specific server, you'll need to change the constants inside the [constants.json](https://github.com/HuzzNZ/Shiro/blob/master/constants.json) file to match them for your server. I recommend replacing all of channel / role IDs as they are crucial for some functions to work.

If you are starting a server and are intending to use this bot, I highly recommend building the server around this bot's required channels and roles as it introduces many channels that wouldn't otherwise be in the server.

Please note that the `waifu_start` and the `waifu_end` roles are always on the bottom of the role hierarchy, right above the `@everyone` role, with `waifu_start` being above `waifu_end`.

### Prerequisites

This bot uses some external API wrappers for reddit and google translate. All of the prerequisites required is listed here below:
* `discord`
* `aiohttp` (`discord` prerequisite)
* `asyncio` (`discord` prerequisite)
* `requests`
* `praw`
* `googletrans`
* `schedule`

These packages can all be installed using `pip`:

```
pip install discord
pip install requests
pip install praw
pip install googletrans
pip install schedule
```

### Adapting the bot

Changing all the Channel / Role IDs under [constants.json](https://github.com/HuzzNZ/Shiro/blob/master/constants.json) adapts the full features of the bot to your server. Please make sure you have changed all the Channel / Role IDs inside the file.

### Creating the Credentials File

A hidden credentials file is not on the repository because of security. You can create this required file by creating a new `JSON` file named `.creds.json` (with the opening period). Inside, include these information:

```json
{
  "token": "{{Discord Bot Token}}",
  "reddit": {
    "client_id": "{{14-char Reddit Script Client ID}}",
    "client_secret": "{{27-char Reddit Script Client Secret}}",
    "password": "{{Reddit Developer Account Password}}",
    "user_agent":"{{This can be anything}}",
    "username": "{{Reddit Developer Account Username}}"
  }
}
```

### End Output

```
[2019-05-16 07:48:48.164138][Bot Client] Starting process
[2019-05-16 07:48:56.532095][...       ] Logged into Reddit as {{Reddit Developer Account}}
[2019-05-16 07:48:56.977434][...       ] Refreshing 24h
[2019-05-16 07:49:15.006144][...       ] Refreshing Embeds
[2019-05-16 07:49:16.265527][...       ] Refreshing Roles
[2019-05-16 07:49:16.278074][...       ] Refreshing Role Embeds
[2019-05-16 07:49:19.077455][...       ] Refreshing Presence
[2019-05-16 07:49:19.078684][...       ] !! Startup Process Finished !!
```

If something goes wrong, please check that you have replaced all the contents of [constants.json](https://github.com/HuzzNZ/Shiro/blob/master/constants.json) and that you have followed the format above for the `.creds.json` file that you will need to create.

## Built With

* [discord.py](https://github.com/Rapptz/discord.py) - Python API Wrapper for Discord
* [PRAW](https://praw.readthedocs.io/en/latest/) - Python API Wrapper for Reddit
* [googletrans](https://pypi.org/project/googletrans/) - Python API Wrapper for Google Translate
* [schedule](https://pypi.org/project/schedule/) - Python Library for scheduling events

## Authors

* **Huzz#0002** - *Code* - [GitHub](https://github.com/HuzzNZ)

## License

This project is licensed under the MIT License.

## Acknowledgments

* Thanks to Rapptz for the comprehensive Discord Python API Library, and the discord.py community for helping me with the code.
* Thanks to the moderators and members of my server for troubleshooting, and finding bugs in Shiro's code.
