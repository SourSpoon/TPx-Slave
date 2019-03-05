import discord
from discord.ext import commands

from cogs.utils.postgresql import SQL
from cogs.utils.convert import RSN


class Names(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: SQL = bot.database
        self.ids = self.bot.ids

    @commands.command()
    async def set_rsn(self, ctx, *, runescape_name: RSN):  # type RSN is actually a str, see convert.py
        """
        Changes the name we have on file for you,
        RSNs must be between 3 and 12 characters containing only Alpha-Numeric characters and spaces
        """
        await self.db.add_user(ctx.author.id, runescape_name)
        await ctx.author.edit(nick=runescape_name)
        unverified_role = discord.utils.get(ctx.guild.roles, id=self.ids['unknown_rsn'])
        if unverified_role in ctx.author.roles:
            await ctx.author.remove_roles(unverified_role)
        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command()
    @commands.has_any_role('Events Team', 'Senior Staff', 'Co-Leader', 'Leader')
    async def force_rsn(self, ctx, target:discord.Member, *, runescape_name:RSN):
        """
        Allows the TPx Staff team to change someone's primary runescape name.
        Target can be a mention, nickname, username or ID. Mentions or IDs are recommended
        Locked to Events Team/ Senior Staff/ Co-Leader/ Leader
        """
        await self.db.add_user(target.id, runescape_name)
        await target.edit(nick=runescape_name)
        unverified_role = discord.utils.get(ctx.guild.roles, id=self.ids['unknown_rsn'])
        await target.remove_roles(unverified_role)
        if unverified_role in target.roles:
            await target.remove_roles(unverified_role)
        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.group(invoke_without_command=True)
    async def points(self, ctx, target: discord.Member = None):
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
    async def points_add(self, ctx, target:discord.Member, value:int, *, reason=None):
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
        await self.bot.dispatch("pvm_points_update", new_points, value, target.id, ctx.message.author.id)

    @commands.command()
    @commands.has_any_role('Events Team', 'Senior Staff', 'Co-Leader', 'Leader')
    async def bulk_add(self, ctx, value:int, reason, *targets:discord.Member):
        """
        A tool for adding points to multiple people
        Target can be a mention, nickname, username or ID. Mentions or IDs are recommended
        Reason is a mandatory field, and should be in quotes "like this"
        Value is the amount of points to add, can be a negative number to remove
        Locked to Events Team/ Senior Staff/ Co-Leader/ Leader
        """
        response = '```\n'
        for t in targets:
            new_points = await self.db.add_points(t.id, value, ctx.author.id, reason)
            response = '{0}{1} now has {2:,}\n'.format(response, t.display_name, new_points)
            await self.bot.dispatch("pvm_points_update", new_points, value, t.id, ctx.message.author.id)
        await ctx.send(f'{response}```')


def setup(bot):
    bot.add_cog(Names(bot))
