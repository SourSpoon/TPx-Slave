import asyncio
import re

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


class Drops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: SQL = bot.database
        self.ids = self.bot.ids

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        Using raw reactions because event will not trigger if message is not in cache.
        Collects the appropriate Objects and fetches message from discord.
        """
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        member: discord.Member = guild.get_member(payload.user_id)
        channel: discord.TextChannel = guild.get_channel(payload.channel_id)
        message: discord.Message = await channel.get_message(payload.message_id)
        emoji: discord.PartialEmoji = payload.emoji
        if member.bot:
            return  # ignore bot reactions
        if not any(r.id == self.ids['events_team'] for r in member.roles):
            return
        if payload.channel_id == self.ids['pvm_drop']:
            return await self.pvm_point_submission(guild, member, channel, message, emoji)

    async def pvm_point_submission(self, guild, member, channel, message, emoji: discord.PartialEmoji):
        """
        Inserts into database with a PvM point value corresponding with the emoji added
        Multiple Emoji can be added for strange point values.
        """
        try:
            points = PVM_POINT_VALUES[emoji.name]
        except KeyError:
            return await self.bot.error_channel.send(f"""
            KEY ERROR WHEN GIVING PVM POINTS TO PLAYER
            message: {message.jump_url}
            """)
        new_points = await self.database.add_points(message.author.id, points, member.id, message.jump_url)
        await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        self.bot.dispatch("pvm_points_update", new_points, points, member.id, message.author.id)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Filters messages based on channel
        """
        if message.author.bot:  # as always ignore bot messages.
            return
        if message.channel.id == self.ids['pvm_drop']:
            return await self.pvm_drop_submission(message)
        if message.channel.id == self.ids['rsn_post']:
            return await self.rsn_posted(message)

    async def pvm_drop_submission(self, message:discord.Message):
        """
        Adds Emojis to new posts in the Drop submissions Channel,
        makes interacting with pvm_point_submission easier
        """
        for emoji_id in PVM_POINT_EMOJI:
            emoji = self.bot.get_emoji(emoji_id)
            await message.add_reaction(emoji)

    async def rsn_posted(self, message: discord.Message):
        """
        Logs people's RSN in the database
        """
        if not re.match(r'^[a-zA-Z0-9 _]{3,12}$', message.content):
            await message.delete()
            await message.channel.send(f'{message.content} is an invalid runescape name', delete_after=20)
        else:
            await self.database.add_user(message.author.id, message.content)
            await message.author.edit(nick=message.content)
            try:
                unknown_rsn_role = discord.utils.get(message.guild.roles, id=self.ids['unknown_rsn'])
                await message.author.remove_roles(unknown_rsn_role)
            except discord.HTTPException:
                await self.bot.error_channel.send(f'cant remove "UNKNOWN RSN" role from "{message.author}"')
        await asyncio.sleep(5)
        await message.delete()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Assigns new Members the Unknown RSN role.
        """
        if member.guild.id != self.ids['tpx_guild']:
            return
        unknown_rsn_role = discord.utils.get(member.guild.roles, id=self.ids['unknown_rsn'])
        await member.add_roles(unknown_rsn_role)

    @commands.Cog.listener()
    async def on_member_leave(self, member):
        if discord.utils.get(member.roles, id=self.bot.ids['unknown_rsn']):
            return  # ignore people who aren't committed/ in the cc
        ch = member.guild.get_channel(self.bot.ids['left_channel'])
        rsn = self.database.get_rsn(member.id)
        await ch.send(f'```\n{member} has left\nRSN: {rsn}```')

    @commands.Cog.listener()
    async def on_pvm_points_update(self, current, added, target, moderator):
        tpx: discord.Guild = self.bot.get_guild(self.bot.ids['tpx_guild'])
        channel: discord.TextChannel = tpx.get_channel(self.bot.ids['pvm_log_channel'])
        mod = tpx.get_member(moderator)
        member = tpx.get_member(target)
        em = discord.Embed(description=f'```\n{member} ({member.display_name}) was credited with {added} pvm points```')
        em.add_field(name='Moderator', value=f'{mod}')
        em.add_field(name='Total Points', value=f'{current}')
        await channel.send(embed=em)



def setup(bot):
    bot.add_cog(Drops(bot))
