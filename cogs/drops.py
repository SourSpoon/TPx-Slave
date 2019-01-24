import asyncio

import discord
from discord.ext import commands

from cogs.utils.postgresql import SQL

PVM_POINT_VALUES = {
    'PVM_5': 5,
    'PVM_10': 10,
    'PVM_25': 25,
    'PVM_50': 50,
    'PVM_100': 100,
    'PVM_250': 250
}

PVM_POINT_EMOJI = [535616389570887698, 535616389357240321, 535616389705236500,
                   535616389692653578, 535616389436670004, 535616389688328203]


class Drops:
    def __init__(self, bot):
        self.bot = bot
        self.database: SQL = bot.database

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        member: discord.Member = guild.get_member(payload.user_id)
        channel: discord.TextChannel = guild.get_channel(payload.channel_id)
        message: discord.Message = await channel.get_message(payload.message_id)
        emoji: discord.PartialEmoji = payload.emoji
        if member.bot:
            return  # ignore bot reactions
        if not any(r.id == 484776707749052426 for r in member.roles):
            return
        if payload.channel_id == 536354503763558411:
            return await self.pvm_point_submission(guild, member, channel, message, emoji)

    async def pvm_point_submission(self, guild, member, channel, message, emoji: discord.PartialEmoji):
        try:
            points = PVM_POINT_VALUES[emoji.name]
        except KeyError:
            return await self.bot.error_channel.send(f"""
            KEY ERROR WHEN GIVING PVM POINTS TO PLAYER
            message: {message.jump_url}
            """)
        await self.database.add_points(message.author.id, points, member.id, message.jump_url)

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id == 536354503763558411:
            return await self.pvm_drop_submission(message)
        if message.channel.id == 536669576507818013:
            return await self.rsn_posted(message)

    async def pvm_drop_submission(self, message:discord.Message):
        for emoji_id in PVM_POINT_EMOJI:
            emoji = self.bot.get_emoji(emoji_id)
            await message.add_reaction(emoji)

    async def rsn_posted(self, message: discord.Message):
        if len(message.content) > 12:
            await message.delete()
            await message.channel.send(f'{message.content} is an invalid runescape name', delete_after=20)
        else:
            await self.database.add_user(message.author.id, message.content)
            await message.author.edit(nick=message.content)
            try:
                unknown_rsn_role = discord.utils.get(message.guild.roles, id=536658901203025941)
                await message.author.remove_roles(unknown_rsn_role)
            except discord.HTTPException:
                await self.bot.error_channel.send(f'cant remove "UNKNOWN RSN" role from "{message.author}"')
        await asyncio.sleep(5)
        await message.delete()

    async def on_member_join(self, member):
        if member.guild.id != 484758564485988374:
            return
        unknown_rsn_role = discord.utils.get(member.guild.roles, id=536658901203025941)
        await member.add_roles(unknown_rsn_role)


def setup(bot):
    bot.add_cog(Drops(bot))
