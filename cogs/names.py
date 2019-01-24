import discord
from discord.ext import commands

from cogs.utils.postgresql import SQL
from cogs.utils.convert import RSN

class Names:
    def __init__(self, bot):
        self.bot = bot
        self.db:SQL = bot.database

    @commands.command()
    async def set_rsn(self, ctx, *, runescape_name:RSN):
        """
        Changes the name we have on file for you,
        RSNs must be between 3 and 12 characters containing only Alpha-Numeric characters and spaces
        """
        await self.db.add_user(ctx.author.id, runescape_name)
        await ctx.author.edit(nick=runescape_name)
        unverified_role = discord.utils.get(ctx.guild.roles, id=536658901203025941)
        if unverified_role in ctx.author.roles:
            await ctx.author.remove_roles(unverified_role)

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
        unverified_role = discord.utils.get(ctx.guild.roles, id=536658901203025941)
        await target.remove_roles(unverified_role)
        if unverified_role in target.roles:
            await target.remove_roles(unverified_role)

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
        await ctx.send(f'{target.display_name} has {points} pvm points')

    @points.command(name='add')
    @commands.has_any_role('Events Team', 'Senior Staff', 'Co-Leader', 'Leader')
    async def points_add(self, ctx, target:discord.Member, value:int, *, reason=None):
        """
        Adds Points To Target
        Target can be a mention, nickname, username or ID. Mentions or IDs are recommended
        Value is the ammount of points to add, can be a negative number to remove
        Locked to Events Team/ Senior Staff/ Co-Leader/ Leader
        """
        if reason is None:
            reason = ctx.message.jump_url
        new_points = await self.db.add_points(target.id, value, ctx.author.id, reason)
        await ctx.send(f'{target.display_name} now has {new_points} PvM Points')

    @commands.command()
    @commands.has_any_role('Events Team', 'Senior Staff', 'Co-Leader', 'Leader')
    async def bulk_add(self, ctx, value:int, reason, *targets:discord.Member):
        """
        A tool for adding points to multiple people
        Target can be a mention, nickname, username or ID. Mentions or IDs are recommended
        Reason is a mandatory field, and should be in quotes "like this"
        Value is the ammount of points to add, can be a negative number to remove
        Locked to Events Team/ Senior Staff/ Co-Leader/ Leader
        """
        response = '```\n'
        for t in targets:
            new_points =  await self.db.add_points(t.id, value, ctx.author.id, reason)
            response = f'{response}{t.display_name} now has {new_points}\n'
        await ctx.send(f'{response}```')


def setup(bot):
    bot.add_cog(Names(bot))
