import datetime
import traceback

import discord
from discord.ext import commands


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

        ignored = (commands.CommandNotFound, commands.UserInputError, commands.MissingPermissions)

        if isinstance(error, ignored):
            return

        handler = {
            discord.Forbidden: '**I do not have the required permissions to run this command.**',
            commands.DisabledCommand: f'{ctx.command} has been disabled.',
            commands.NoPrivateMessage: f'{ctx.command} can not be used in Private Messages.',
            commands.CheckFailure: '**You aren\'t allowed to use this command!**'
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