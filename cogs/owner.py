from discord.ext import commands
import traceback
import discord
import textwrap
from contextlib import redirect_stdout
import io
import random

# to expose to the eval command
import datetime
from collections import Counter
import inspect
import asyncio


class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command(pass_context=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command()
    async def pick_winner(self, ctx, channel: discord.TextChannel, message_id: int, emoji: discord.Emoji):
        message = await channel.get_message(message_id)
        for r in message.reactions:
            if r.emoji == emoji:
                reaction = r
                break
        else:
            return await ctx.send('No Matching Emoji')
        users = await reaction.users().flatten()
        winner = random.choice(users)
        await ctx.send(f'{winner.mention} has been picked')

    @commands.command(aliases=['logoff', 'reboot', 'shutdown'])
    async def logout(self, ctx):
        await ctx.message.add_reaction('\N{SPOON}')
        await self.bot.logout()

    @commands.command(name='load')
    async def _load(self, ctx, *, cog: str):
        """Loads a module."""

        cog = f'cogs.{cog.lower()}'
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send(f'{type(e).__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload')
    async def _reload(self, ctx, *, cog: str):
        """Reloads a module."""

        cog = f'cogs.{cog.lower()}'
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send(f'{type(e).__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='unload')
    async def _unload(self, ctx, *, cog: str):
        """Unloads a module."""

        cog = f'cogs.{cog.lower()}'
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send(f'{type(e).__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')


def setup(bot):
    bot.add_cog(Owner(bot))
