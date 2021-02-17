import logging

import discord
from redbot.core import Config, commands, modlog
from redbot.core.i18n import Translator, cog_i18n
from redbot.core.commands import Context
from typing import List

from .events import UserValidationEvents
from .pastebin import send, chan_dump

log = logging.getLogger("red.customcogs.uservalidation")
_ = Translator("RoleTools", __file__)


@cog_i18n(_)
class UserValidation(UserValidationEvents, commands.Cog):
    """
    User Validation for SafePlace discord server
    """

    __author__ = ["Celi28"]
    __version__ = "1.0.0"

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=30397250846178114, force_registration=True)
        self.config.register_global(version="1.0.0")
        default_guild = {
            "validation_channel_id": "",
            "validation_messages": {},
            "validation_tmp_channel": {},
            "pastebin_apikey": "",
            "pastebin_username": "",
            "pastebin_password": ""
        }
        self.config.register_guild(**default_guild)

    async def initialize(self):
        await self.register_casetypes()

    @staticmethod
    async def register_casetypes():
        # Registering a single casetype
        valid_case = {
            "name": "valid",
            "default_setting": True,
            "image": "✔️",
            "case_str": "Validation",
        }
        try:
            await modlog.register_casetype(**valid_case)
        except RuntimeError:
            pass

    @commands.group()
    async def uservalidation(self, ctx: Context):
        """
        User Validation commands
        """
        pass

    @uservalidation.command()
    @commands.admin()
    async def channel(self, ctx: Context, *, channel: discord.TextChannel):
        """
        Setup the validation TextChannel
        """
        print("setup", channel.id)
        await self.config.guild(ctx.guild).validation_channel_id.set(channel.id)
        return await ctx.send(_("{channel} is set as the validation channel").format(channel=channel.name))

    @commands.command()
    @commands.admin_or_permissions(manage_messages=True)
    async def valid(self, ctx: Context):
        """
        Validate a user from a user-validation channel
        :param ctx: Context
        :return: None
        """
        async with self.config.guild(ctx.guild).validation_tmp_channel() as validation_channels:
            chan_to_remove: discord.TextChannel = ctx.channel
            user_to_edit: discord.Member = ctx.guild.get_member(validation_channels[str(chan_to_remove.id)])

        await user_to_edit.add_roles(ctx.guild.get_role(808732077565542420))

        title = str(user_to_edit.id) + " - Accueil Validation"

        data = await chan_dump(chan_to_remove)
        url = await send(ctx, self.config, title, data)

        keywords = {"author_name": user_to_edit.name,
                    "url": url,
                    "author_id": user_to_edit.id}

        message_validation = "```VALIDATION - {author_name} - {author_id}\nURL: {url}```".format(**keywords)
        validation_channel_id = await self.config.guild(ctx.guild).validation_channel_id()
        validation_channel: discord.TextChannel = ctx.guild.get_channel(validation_channel_id)
        await validation_channel.send(content=message_validation)
        await chan_to_remove.delete(reason="Validation de l'utilisateur - " + user_to_edit.name)
        await modlog.create_case(
            self.bot, ctx.guild, ctx.message.created_at, "valid", user_to_edit,
            ctx.author, "Accueil validation", channel=validation_channel)

    @commands.command()
    @commands.admin_or_permissions(manage_messages=True)
    async def kvalid(self, ctx: Context, *, reason: str):
        """
        Kick user from server
        :param ctx: Context
        :param reason: The reason of the kick
        :return: None
        """
        async with self.config.guild(ctx.guild).validation_tmp_channel() as validation_channels:
            chan_to_remove: discord.TextChannel = ctx.channel
            user_to_edit: discord.Member = ctx.guild.get_member(validation_channels[str(chan_to_remove.id)])

        title = str(user_to_edit.id) + " - Accueil Validation"

        data = await chan_dump(chan_to_remove)
        url = await send(ctx, self.config, title, data)

        keywords = {"author_name": user_to_edit.name,
                    "url": url,
                    "author_id": user_to_edit.id}

        message_validation = "```KICK - {author_name} - {author_id}\nURL: {url}```".format(**keywords)
        validation_channel_id = await self.config.guild(ctx.guild).validation_channel_id()
        validation_channel: discord.TextChannel = ctx.guild.get_channel(validation_channel_id)
        await validation_channel.send(content=message_validation)
        if not reason:
            reason = "Echec de la validation - "
        await ctx.guild.kick(user_to_edit, reason=reason)
        await chan_to_remove.delete(reason="kick de l'utilisateur - " + user_to_edit.name)
        await modlog.create_case(
            self.bot, ctx.guild, ctx.message.created_at, "kick", user_to_edit,
            ctx.author, reason, channel=validation_channel)

    @commands.command()
    @commands.admin_or_permissions(manage_messages=True)
    async def bvalid(self, ctx: Context, *, reason: str):
        """
        Kick user from server
        :param ctx: Context
        :param reason: The reason of the kick
        :return: None
        """
        async with self.config.guild(ctx.guild).validation_tmp_channel() as validation_channels:
            chan_to_remove: discord.TextChannel = ctx.channel
            user_to_edit: discord.Member = ctx.guild.get_member(validation_channels[str(chan_to_remove.id)])

        title = str(user_to_edit.id) + " - Accueil Validation"

        data = await chan_dump(chan_to_remove)
        url = await send(ctx, self.config, title, data)

        keywords = {"author_name": user_to_edit.name,
                    "url": url,
                    "author_id": user_to_edit.id}

        message_validation = "```BAN - {author_name} - {author_id}\nURL: {url}```".format(**keywords)
        validation_channel_id = await self.config.guild(ctx.guild).validation_channel_id()
        validation_channel: discord.TextChannel = ctx.guild.get_channel(validation_channel_id)
        await validation_channel.send(content=message_validation)
        if not reason:
            reason = "Echec de la validation - "
        await ctx.guild.ban(user_to_edit, delete_message_days=0, reason=reason)
        await chan_to_remove.delete(reason="ban de l'utilisateur - " + user_to_edit.name)
        await modlog.create_case(
            self.bot, ctx.guild, ctx.message.created_at, "ban", user_to_edit,
            ctx.author, reason, channel=validation_channel)

    @commands.group()
    async def pastebin(self, ctx: Context):
        """
        Pastebin configuration and instanciation
        :param ctx: Context
        :return: None
        """
        pass

    @pastebin.command()
    @commands.admin()
    async def config(self, ctx: Context, apikey: str, username: str, *, password: str, ):
        await self.config.guild(ctx.guild).pastebin_apikey.set(apikey)
        await self.config.guild(ctx.guild).pastebin_username.set(username)
        await self.config.guild(ctx.guild).pastebin_password.set(password)
        await ctx.send("Done !")

    @pastebin.command()
    @commands.admin()
    async def send(self, ctx: Context, title: str, *, content: str):
        url = await send(ctx, self.config, title, content)
        await ctx.send(url)
