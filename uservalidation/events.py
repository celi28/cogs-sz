import logging

import discord
import datetime
from redbot.core import Config, commands, modlog
from redbot.core.bot import Red

log = logging.getLogger("red.customcogs.uservalidation")


class UserValidationEvents:

    bot: Red
    config: Config

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

        message_validation = "```Username: {author_name}\nAge: {author_age} jours\nId: {author_id}```".format(**keywords)

        sent_message: discord.Message = await message.channel.send(content=message_validation)
        async with self.config.guild(guild).validation_messages() as validation_messages:
            validation_messages[sent_message.id] = message.author.id

        await sent_message.add_reaction('✅')
        await sent_message.add_reaction('❓')
        await sent_message.add_reaction('❌')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild_id = getattr(payload, "guild_id", None)
        if not guild_id:
            return
        if payload.member.bot:
            return
        mod = False
        for role in payload.member.roles:
            if role.id == 807995697680613416 or role.id == 807954178210922526:
                mod = True
        if not mod:
            return

        guild_settings = await self.config.guild(self.bot.get_guild(guild_id)).validation_channel_id()
        if payload.channel_id != guild_settings:
            return

        guild_involved: discord.Guild = self.bot.get_guild(payload.guild_id)
        channel_involved: discord.TextChannel = guild_involved.get_channel(payload.channel_id)
        message_involved: discord.Message = await channel_involved.fetch_message(payload.message_id)
        async with self.config.guild(guild_involved).validation_messages() as validation_message:
            user_involved: discord.Member = guild_involved.get_member(validation_message[str(payload.message_id)])

        if str(payload.emoji) == '✅':
            await user_involved.add_roles(guild_involved.get_role(808732077565542420))
        elif str(payload.emoji) == '❓':
            category_linked: discord.CategoryChannel = guild_involved.get_channel(807978619410448454)

            overwrites = {
                guild_involved.default_role: discord.PermissionOverwrite(read_messages=False),
                guild_involved.get_role(807995697680613416): discord.PermissionOverwrite(read_messages=True),
                user_involved: discord.PermissionOverwrite(read_messages=True)
            }
            validation_channel: discord.TextChannel = await category_linked.create_text_channel(
                "validation-{user}".format(user=user_involved.name), overwrites=overwrites)
            async with self.config.guild(guild_involved).validation_tmp_channel() as validation_tmp_channel:
                validation_tmp_channel[validation_channel.id] = user_involved.id

            msg_to_send = "Bonjour {user} ".format(user=user_involved.mention) +\
                          "vous avez été convié ici par la modération afin de discuter avec vous.\n" +\
                          "Merci de patienter quelques instant, et de répondre aux questions posées"
            await validation_channel.send(content=msg_to_send)

        else:
            await guild_involved.ban(user_involved, delete_message_days=0, reason="Echec de la validation")
            await modlog.create_case(
                self.bot, guild_involved, message_involved.created_at, "Ban 🔨", user_involved,
                payload.member, "Echec de la validation", channel=channel_involved)

        for reaction in message_involved.reactions:
            async for user in reaction.users():
                if user.id == payload.member.id:
                    continue
                await reaction.clear()
        await message_involved.add_reaction('☑️')
