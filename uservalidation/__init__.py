from .uservalidation import UserValidation


async def setup(bot):
    cog = UserValidation(bot)
    await cog.initialize()
    bot.add_cog(cog)