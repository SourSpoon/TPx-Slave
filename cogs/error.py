import datetime
import traceback

import discord
from discord.ext import commands


class BadRunescapeName(commands.UserInputError):
    """
    Exception raised when a string can not be converted to a Runescape character name:
    ^[a-zA-Z0-9 _]{3,12}$
    Runescape names can technically be fewer than 3 characters with a true minimum of one alphanumeric.
    """
    pass


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_channel = self.bot.error_channel

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            attr = f'_{cog.__class__.__name__}__error'
            if hasattr(cog, attr):
                return

        error = getattr(error, 'original', error)

        ignored = (commands.CommandNotFound, commands.MissingPermissions)

        if isinstance(error, ignored):
            return

        handler = {
            discord.Forbidden: '**I do not have the required permissions to run this command.**',
            commands.DisabledCommand: f'{ctx.command} has been disabled.',
            commands.NoPrivateMessage: f'{ctx.command} can not be used in Private Messages.',
            commands.CheckFailure: '**You aren\'t allowed to use this command!**',
            commands.TooManyArguments: f'Too many arguments, try wrapping singular arguments in quotes or check ^help {ctx.command}',
            commands.BadArgument: f'Can\'t convert one of your arguments, did you get them in the correct order?, check ^help {ctx.command}',
            commands.MissingRequiredArgument: f'Missing one (or some) required arguments,check ^help {ctx.command}',
            BadRunescapeName: f'That is not a valid Runescape name, Runescape names must only contain Alphanumeric'
                                  f' characters and a space, be a maximum of 12 characters long and be at least 3 characters'
                                  f' if you have a name shorter than 3 characters please contact a mod to verify.'
        }
        try:
            message = handler[type(error)]
        except KeyError:
            pass
        else:
            return await ctx.send(message)

        embed = discord.Embed(title=f'Command Exception', color=discord.Color.red())
        embed.set_footer(text='Occurred on')
        embed.timestamp = datetime.datetime.utcnow()

        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
        exc = exc.replace('`', '\u200b`')
        embed.description = f'```py\n{exc}\n```'

        embed.add_field(name='Command', value=ctx.command.qualified_name)
        embed.add_field(name='Invoker', value=ctx.author)
        embed.add_field(name='Location', value=f'Guild: {ctx.guild}\nChannel: {ctx.channel}')
        embed.add_field(name='Message', value=ctx.message.content)
        await self.error_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))