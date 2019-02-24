import random

import discord
from discord.ext import commands


class EventsTeam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pick(self, ctx, *names):
        """
        picks a random name from the list of names, useful for giveaways and such.

        Not currently locked down, or anything fancy. names can be any collection of strings.
        names are seperated by spaces, so names with spaces inside them will need to be wrapped in quotes, like
        ^pick MediocreMatt "B R II A N" SourSpoon
        """
        await ctx.send(f'I have picked: {random.choice(names)}')


def setup(bot):
    bot.add_cog(EventsTeam(bot))
