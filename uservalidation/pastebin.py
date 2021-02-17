from typing import List

import discord
import requests

from redbot.core import Config
from redbot.core.commands import Context


async def send(ctx: Context, config: Config, title: str, content: str) -> str:
    """
    Send the data to Pastebin
    :return: the URL of the pastebin
    """

    pastbin_config = {
        "api_dev_key": await config.guild(ctx.guild).pastebin_apikey(),
        "api_user_name": await config.guild(ctx.guild).pastebin_username(),
        "api_user_password": await config.guild(ctx.guild).pastebin_password()
    }

    data = {
        'api_option': 'paste',
        'api_dev_key': pastbin_config["api_dev_key"],
        'api_paste_format': 'email',
        'api_paste_code': content,
        'api_paste_name': title,
        'api_paste_expire_date': 'N',
        'api_user_key': ""
    }

    login = requests.post("https://pastebin.com/api/api_login.php", data=pastbin_config)
    if login.status_code != 200:
        raise ConnectionRefusedError("API login failed: " + str(login.status_code))
    data['api_user_key'] = login.text

    r = requests.post("https://pastebin.com/api/api_post.php", data=data)
    if r.status_code != 200:
        raise ConnectionRefusedError("API post failed: " + str(r.status_code))

    return r.text


async def chan_dump(chan_to_remove: discord.TextChannel) -> str:
    messages_raw: List[discord.Message] = await chan_to_remove.history(oldest_first=True).flatten()
    output = ""
    for message in messages_raw:
        if message.author.display_name != message.author.name:
            author = message.author.display_name + " - <" + message.author.name + ">"
        else:
            author = "<" + message.author.name + ">"
        text = message.content
        output += author + "\r\n" + text + "\r\n\r\n"

    return output
