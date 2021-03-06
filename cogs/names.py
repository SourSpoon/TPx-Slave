import asyncio

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


def setup(bot):
    bot.add_cog(Names(bot))
