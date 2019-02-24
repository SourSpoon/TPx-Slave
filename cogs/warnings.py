import discord
from discord.ext import commands

colours = {1: 0xFFFF00, 2: 0xFF7F00, 3: 0xFF0000}


def warning_embed_builder(ctx, target, severity, reason, messaged_user):
    embed = discord.Embed(colour=colours[severity], title='Warning Issued', description=f'```{reason}```')
    embed.add_field(name='Offender:', value=f'{target.mention}')
    embed.add_field(name='Severity:', value=f'{severity}')
    embed.add_field(name='Moderator:', value=f'{ctx.author.mention}')
    if messaged_user:
        embed.add_field(name='Offender Notified', value='Yes')
    else:
        embed.add_field(name='Offender Notified', value='No')
    return embed


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    async def cog_check(self, ctx):
        return bool(discord.utils.get(ctx.author.roles, id=self.bot.ids['events_team']))

    @commands.command()
    async def warn(self, ctx, target: discord.Member, severity: int, *, reason):
        """
        Target can be a mention, nickname, username or ID. Mentions or IDs are recommended
        Reason is a mandatory field, and should be in quotes "like this"
        Severity is a mandatory field and should be a number between 1 and 3, 3 being more severe
        Locked to Events Team/ Senior Staff/ Co-Leader/ Leader
        """
        if not 1 <= severity <= 3:
            return await ctx.send('Severity must be between 1 and 3')
        warns_channel = ctx.guild.get_channel(self.bot.ids['warns_channel'])
        try:
            await target.send(f'You have been warned by {ctx.author} with a severity of {severity} '
                               f'for the following reason:\n ```\n{reason}```\nif you wish to dispute this '
                               f'please appeal to one of the leaders')
            em = warning_embed_builder(ctx, target, severity, reason, True)
            await warns_channel.send(embed=em)

        except discord.errors.Forbidden:
            em = warning_embed_builder(ctx, target, severity, reason, False)
            await warns_channel.send(embed=em)

        finally:
            await self.database.add_warning(target.id, severity, ctx.author.id, reason)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')


def setup(bot):
    bot.add_cog(Warn(bot))
