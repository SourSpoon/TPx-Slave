# TPx-Slave
This bot was largely written in a short amount of time, using my own [template](https://github.com/SourSpoon/Discord.py-Template) and using some of [R. Danny's](https://github.com/Rapptz/RoboDanny) code (such as Eval, and it's general structure)

Requirements:
Python 3.6
PostgreSQL 10
Discord\.py [Source](https://github.com/Rapptz/discord.py) [Docs](https://discordpy.readthedocs.io/en/latest/index.html) (tested on v1.1)

It also uses Async PG [Source](https://github.com/MagicStack/asyncpg) [Docs](https://magicstack.github.io/asyncpg/current/) (tested on v0.18.3)

And while this has been tested on PSQL v10 and Ubuntu 18.04 with python 3.6 I don't see why you couldnt use python 3.7 or PSQL 11

If you create your own copy of this bot you will need to create your own JSON config file in the format:
```json
{
"token": "discord_bot_user_token",
"description": "a brief description of the application, this appears on the help menu",
"postgres":{
	"user": "postgres_user_name",
	"database": "database name",
	"password": "postgres_user_password",
	"host": "postgres_database_ip"
	}
}
```
this should be saved as `cfg/secrets.json`

Should you want to customise this yourself, you will need to know that
* the dictionary in `main.py` that contains IDs will need to have your own IDs in
* the list of emoji names and ids in `/cogs/drops.py` will need to have your own ids & emoji names
* the database uses 32 bit signed ints, so you will get errors saying "integer out of range" if you try to insert values larger than 2.14 billion.
 You can either use bigints, which increases space used on disk or lose precision by dividing the value by 10/100/1000 ect. It will have to be a whole number.

In order to aid your database set up I have used pg_dump to  dump the empty database and included it under utils, this can be used to restore the empty database.
(it creates a database called "discord" with a role "discord" as the owner, you may need to create the role first)

As far as running the bot, unless you are on some mega discord server, this should run quite happily with 1 vCore and 1GB of RAM. You could probably get by with 512mb, but I would recommend 1GB.
