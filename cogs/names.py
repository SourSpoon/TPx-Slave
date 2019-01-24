import discord
from discord.ext import commands

from cogs.utils.postgresql import SQL


class Names:
    def __init__(self, bot):
        self.bot = bot
        self.db:SQL = bot.database

    @commands.command()
    async def set_rsn(self, ctx, *, runescape_name):
        if len(runescape_name) > 12:
            return await ctx.send('Runescape Name Invalid, Can not exceed 12 characters')
        await self.db.add_user(ctx.author.id, runescape_name)
        await ctx.author.edit(nick=runescape_name)
        unverified_role = discord.utils.get(ctx.guild.roles, id=536658901203025941)
        if unverified_role in ctx.author.roles:
            await ctx.author.remove_roles(unverified_role)


    @commands.command()
    @commands.has_any_role('Events Team', 'Senior Staff', 'Co-Leader', 'Leader')
    async def force_rsn(self, ctx, target:discord.Member, *, runescape_name):
        if len(runescape_name) > 12:
            await ctx.send('Runescape Names can not be longer than 12 characters')
        await self.db.add_user(target.id, runescape_name)
        await target.edit(nick=runescape_name)
        unverified_role = discord.utils.get(ctx.guild.roles, id=536658901203025941)
        await target.remove_roles(unverified_role)
        if unverified_role in target.roles:
            await target.remove_roles(unverified_role)

    @commands.group(invoke_without_command=True)
    async def points(self, ctx, target: discord.Member = None):
        if target is None:
            target = ctx.author
        points = await self.db.get_pvm_points(target.id)
        await ctx.send(f'{target.display_name} has {points} pvm points')

    @points.command(name='add')
    @commands.has_any_role('Events Team', 'Senior Staff', 'Co-Leader', 'Leader')
    async def points_add(self, ctx, target:discord.Member, value:int, *, reason=None):
        if reason is None:
            reason = ctx.message.jump_url
        new_points = await self.db.add_points(target.id, value, ctx.author.id, reason)
        await ctx.send(f'{target.display_name} now has {new_points} PvM Points')



def setup(bot):
    bot.add_cog(Names(bot))
