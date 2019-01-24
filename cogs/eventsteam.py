import random

import discord
from discord.ext import commands



class EventsTeam:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pick(self, ctx, *names):
        await ctx.send(f'I have picked: {random.choice(names)}')


def setup(bot):
    bot.add_cog(EventsTeam(bot))
