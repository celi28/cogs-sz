import logging

import discord
import datetime
from redbot.core import Config, commands
from redbot.core.bot import Red

log = logging.getLogger("red.customcogs.uservalidation")


class UserValidationEvents:

    bot: Red
    config: Config
    settings: dict

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        guild = getattr(message, "guild", None)
        if not guild:
            return

        guild_settings_id = await self.config.guild(message.guild).validation_channel_id()
        if not guild_settings_id:
            return
        if message.channel.id != guild_settings_id:
            return

        keywords = {"author_name": message.author.name,
                    "author_age": (datetime.datetime.now() - message.author.created_at).days,
                    "author_id": message.author.id}

        message_validation = "```username: {author_name}\nage: {author_age} jours\nid: {author_id}```".format(**keywords)

        sent_message = await message.reply(content=message_validation, mention_author=False)

        valid_cross = self.bot.get_emoji(810225318228131890)
        question = self.bot.get_emoji(810225740016254986)
        deny_cross = self.bot.get_emoji(810226159978545152)

        await sent_message.add_reaction(valid_cross)
        await sent_message.add_reaction(question)
        await sent_message.add_reaction(deny_cross)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild_id = getattr(payload, "guild_id", None)
        if not guild_id:
            return

        guild_settings = await self.config.guild(guild_id).validation_channel_id()
        if payload.channel_id != guild_settings:
            return

        guild_involved: discord.Guild = self.bot.get_guild(payload.guild_id)
        channel_involved: discord.TextChannel = self.bot.get_guild(payload.guild_id)
        message_involved: discord.Message = await channel_involved.fetch_message(payload.message_id)
        user_involved: discord.Member = message_involved.author

        if payload.emoji.id == 810225318228131890:
            await user_involved.add_roles(guild_involved.get_role(808732077565542420))
            # todo: comment user validation
        elif payload.emoji.id == 810225740016254986:
            category_linked: discord.CategoryChannel = guild_involved.get_channel(807978619410448454)

            overwrites = {
                guild_involved.default_role: discord.PermissionOverwrite(read_messages=False),
                guild_involved.get_role(807995697680613416): discord.PermissionOverwrite(read_messages=True)
            }

            validation_channel: discord.TextChannel = await category_linked.create_text_channel(
                "validation-{user}".format(user=user_involved.name), overwrites=overwrites)
            self.settings[payload.guild_id]["validation_channels"].append(validation_channel.id)

            msg_to_send = "Bonjour {user} ".format(user=user_involved.name) +\
                          "vous avez été convié ici par la modération afin de discuter avec vous.\n" +\
                          "Merci de patienter quelques instant, et de répondre aux questions posées"

            await validation_channel.send(content=msg_to_send)

            # todo: Ajouter commandes de validation

        else:
            # todo: ban user and inform modlog
            pass
