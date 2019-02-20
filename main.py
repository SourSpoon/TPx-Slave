import asyncio
import datetime
import json
import logging
from pathlib import Path

import asyncpg
import discord
from discord.ext import commands

from cogs.utils.postgresql import SQL

ids = {
    'pvm_drop': 536354503763558411,
    'rsn_post': 536669576507818013,
    'events_team': 484776707749052426,
    'unknown_rsn': 536658901203025941,
    'tpx_guild': 484758564485988374,
    'error_channel': 536360055079960577,
    'test_guild': 290645427995279360
}

voice_channels = {
    484758564964007939: 'Grand Exchange',
    484767499582439445: 'Lumbridge',
    484783520703709203: 'Falador',
    486188720060497929: 'Draynor Village',
    486188766906679320: 'Yanille',
    517367528800911361: 'Annakarl',
    484784170254729226: 'Mount Karluum',
    484783419687960577: 'Goblin Village',
    484770024121434114: 'NMZ Prods (AFK)',
}



def config_load():
    with open('cfg/secret.json', 'r', encoding='utf-8') as doc:
        #  Please make sure encoding is correct, especially after editing the config file
        return json.load(doc)


async def run():
    """
    Where the bot gets started. If you wanted to create an database connection pool or other session for the bot to use,
    it's recommended that you create it here and pass it to the bot as a kwarg.
    """

    config = config_load()
    asyncpg_pool = await asyncpg.create_pool(**config['postgres'])
    database = SQL(asyncpg_pool)

    bot = Bot(config=config,
              description=config['description'],
              database=database)
    try:
        await bot.start(config['token'])
    except KeyboardInterrupt:
        await bot.logout()


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        print('bot started')
        super().__init__(
            command_prefix=self.get_prefix_,
            description=kwargs.pop('description')
        )
        self.database = kwargs.pop('database')
        self.start_time = None
        self.app_info = None
        self.error_channel = None
        self.voice_channels = voice_channels

        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())
        self.ids = ids
        #  self.loop.create_task(self.rename_channels())

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out uptime.
        """
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def get_prefix_(self, bot, message):
        """
        A coroutine that returns a prefix.
        I have made this a coroutine just to show that it can be done. If you needed async logic in here it can be done.
        A good example of async logic would be retrieving a prefix from a database.
        """
        prefix = ['^']
        return commands.when_mentioned_or(*prefix)(bot, message)

    async def load_all_extensions(self):
        """
        Attempts to load all .py files in /cogs/ as cog extensions
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing
        cogs = [x.stem for x in Path('cogs').glob('*.py')]
        for extension in cogs:
            try:
                self.load_extension(f'cogs.{extension}')
                print(f'loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                print(f'failed to load extension {error}')
            print('-' * 10)

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        print('-' * 10)
        self.app_info = await self.application_info()
        print(f'Logged in as: {self.user.name}\n'
              f'Using discord.py version: {discord.__version__}\n'
              f'Owner: {self.app_info.owner}\n'
              f'Template Maker: SourSpoon / Spoon#7805')
        print('-' * 10)
        self.error_channel = self.get_channel(self.ids['error_channel'])

    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
        always ignore bots.
        """
        await self.error_channel.send('on message triggered')
        if message.author.bot:
            return  # ignore all bots
        if not message.guild:
            return  # ignore all DMs
        if message.channel.id == self.ids['rsn_post'] or message.channel.id == self.ids['pvm_drop']:
            return
        if message.guild.id != self.ids['tpx_guild'] or message.guild.id != self.ids['test_guild']:
            return
        await self.process_commands(message)
        await self.error_channel.send('Message Processed')

    async def rename_channels(self):
        await self.wait_until_ready()
        while True:
            for key, value in self.voice_channels.items():
                channel: discord.VoiceChannel = self.get_channel(key)
                if channel.name == value:
                    continue
                await channel.edit(name=value)
            await asyncio.sleep(86400)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
