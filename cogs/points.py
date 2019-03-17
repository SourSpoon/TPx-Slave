import asyncio
import datetime
import random

import discord
from discord.ext import commands


class Points(commands.Cog):
    """
    A series of commands used to find out who has pvm points and to add/ remove pvm points
    """
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.database

    @commands.group(invoke_without_command=True)
    async def points(self, ctx, *, target: discord.Member = None):
        """
        Used to check someone's PvM points.
        Target is an optional value, if none is provided it will check the message author's points
        Target can be a mention, nickname, username or ID. Mentions or IDs are recommended
        """
        if target is None:
            target = ctx.author
        points = await self.db.get_pvm_points(target.id)
        await ctx.send('{0} now has {1:,} PvM Points'.format(target.display_name, points))

    @points.command(name='add')
    @commands.has_any_role('Events Team', 'Senior Staff', 'Co-Leader', 'Leader')
    async def points_add(self, ctx, target: discord.Member, value: int, *, reason=None):
        """
        Adds Points To Target
        Target can be a mention, nickname, username or ID. Mentions or IDs are recommended
        Value is the amount of points to add, can be a negative number to remove
        Locked to Events Team/ Senior Staff/ Co-Leader/ Leader
        """
        if reason is None:
            reason = ctx.message.jump_url
        new_points = await self.db.add_points(target.id, value, ctx.author.id, reason)
        await ctx.send('{0} now has {1:,} PvM Points'.format(target.display_name, new_points))
        self.bot.dispatch("pvm_points_update", new_points, value, target.id, ctx.message.author.id)

    @commands.command()
    @commands.has_any_role('Events Team', 'Senior Staff', 'Co-Leader', 'Leader')
    async def bulk_add(self, ctx, value:int, reason, *targets: discord.Member):
        """
        A tool for adding points to multiple people
        Target can be a mention, nickname, username or ID. Mentions or IDs are recommended
        Reason is a mandatory field, and should be in quotes "like this"
        Value is the amount of points to add, can be a negative number to remove
        Locked to Events Team/ Senior Staff/ Co-Leader/ Leader
        """
        response = '```\n'
        done = {}
        for t in targets:
            new_points = await self.db.add_points(t.id, value, ctx.author.id, reason)
            response = '{0}{1} now has {2:,}\n'.format(response, t.display_name, new_points)
            done[t.id] = (new_points, value, t.id, ctx.message.author.id)
        await ctx.send(f'{response}```')
        for i in done.values():
            self.bot.dispatch("pvm_points_u", *i)
            await asyncio.sleep(2)  # aid with bot responsiveness/ avoid ratelimits

    @commands.command(name='events_points')
    async def voice_channel_points(self, ctx, channel: discord.VoiceChannel=None):
        """
        Will give points to everyone in a given voice channel. If no channel is specified it will use the voice channel
        you are connected to.
        This will only ever give 15 points for event attendance.
        """
        successful = ''
        dict_success = {}
        failed = ''
        date = datetime.datetime.utcnow()
        date_string = date.strftime('%Y - %m - %d')
        if channel is None and ctx.author.voice:
            channel = ctx.author.voice.voice_channel
        else:
            return await ctx.send('Please either specify a channel or join one')
        for m in channel.members:
            try:
                new_points = await self.db.add_points(m.id, 15, ctx.author.id, f'Event hosted by {str(ctx.author)}'
                                                            f' on {date_string}')
                successful = f'{successful}\n{m.display_name}'
                dict_success[m.id] = (new_points, 15, m.id, ctx.message.author.id)
            except Exception:
                failed = f'{failed}\n{m.display_name}'
        await ctx.send(f'Successful:\n```{successful}`` Failed:\n```{failed}```')
        for i in dict_success.values():
            self.bot.dispatch("pvm_points_update", *i)
            await asyncio.sleep(2)


def setup(bot):
    bot.add_cog(Points(bot))
