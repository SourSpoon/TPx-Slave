import re

import discord
from discord.ext import commands

from cogs.error import BadRunescapeName


class RSN(commands.Converter):
    async def convert(self, ctx, argument):
        runescape_name = re.match(r'^[a-zA-Z0-9 _-]{2,12}$', argument)
        if runescape_name is None:
            raise BadRunescapeName
        return runescape_name.string
