import datetime
import random

import discord
from discord.ext import commands


class EventsTeam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    async def cog_check(self, ctx):
        return discord.utils.get(ctx.author.roles, id=self.bot.ids['events_team'])

    @commands.command()
    async def pick(self, ctx, *names):
        """
        picks a random name from the list of names, useful for giveaways and such.

        Not currently locked down, or anything fancy. names can be any collection of strings.
        names are separated by spaces, so names with spaces inside them will need to be wrapped in quotes, like
        ^pick MediocreMatt "B R II A N" SourSpoon
        """
        await ctx.send(f'I have picked: {random.choice(names)}')

    @commands.command(name='events_points')
    async def voice_channel_points(self, ctx, channel: discord.VoiceChannel=None):
        """
        Will give points to everyone in a given voice channel. If no channel is specified it will use the voice channel
        you are connected to.
        This will only ever give 15 points for event attendance.
        """
        successful = ''
        failed = ''
        date = datetime.datetime.utcnow()
        date_string = date.strftime('%Y - %m - %d')
        if channel is None and ctx.author.voice:
            channel = ctx.author.voice.voice_channel
        else:
            return await ctx.send('Please either specify a channel or join one')
        for m in channel.members:
            try:
                new_points = await self.database.add_points(m.id, 15, ctx.author.id, f'Event hosted by {str(ctx.author)}'
                                                            f' on {date_string}')
                successful = f'{successful}\n{m.display_name}'
                self.bot.dispatch("pvm_points_update", new_points, 15, m.id, ctx.message.author.id)
            except Exception:
                failed = f'{failed}\n{m.display_name}'
        await ctx.send(f'Successful:\n```{successful}`` Failed:\n```{failed}```')


def setup(bot):
    bot.add_cog(EventsTeam(bot))
