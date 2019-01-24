import datetime

import asyncpg


class SQL:
    def __init__(self, pool: asyncpg.pool.Pool):
        self.pool = pool

    async def add_points(self, discord_id: int, points:int, moderator: int, reason: str):
        """
        Inserts data into the SQL database,
        Does the log 1st, incase moderator is invalid and will refuse to add points.
        """
        await self.pool.execute("""
        INSERT INTO pvm_log (discord_id, points_added, moderator, reason, date)
            VALUES ($1, $2, $3, $4, $5)
        
        """, discord_id, points, moderator, reason, datetime.datetime.utcnow())
        new_points = await self.pool.fetchval("""
                UPDATE users
                SET pvm_points = pvm_points + $2
                WHERE discord_id = $1
                RETURNING pvm_points;
                """, discord_id, points)
        return new_points

    async def add_user(self, discord_id: int, rsn: str, ):
        await self.pool.execute("""
        INSERT INTO users (discord_id, runescape_name)
            VALUES ($1, $2)
        ON CONFLICT (discord_id)
        DO UPDATE SET runescape_name = $2;
        """,  discord_id, rsn)

    async def add_warning(self, offender_id, points, moderator, reason):

        await self.pool.execute("""
        INSERT INTO warn_log (offender_id, points_added, moderator, reason, date)
            VALUES ($1, $2, $3, $4, $5)
            """, offender_id, points, moderator, reason, datetime.datetime.utcnow())

        new_warn_points = await self.pool.fetchval("""
                UPDATE users
                SET warn_points = warn_points + $2
                WHERE discord_id = $1
                RETURNING warn_points;
                """, offender_id, points)
        return new_warn_points

    async def get_warn_logs(self, discord_id):
        warning_records = await self.pool.fetch("""
        SELECT * FROM warn_logs
        WHERE offender_id = $1
        ORDER BY timestamp DESC LIMIT 10;
        """, discord_id)
        return warning_records

    async def get_pvm_logs(self, discord_id):
        pvm_records = await self.pool.fetch("""
        SELECT * FROM pvm_logs
        WHERE offender_id = $1
        ORDER BY timestamp DESC LIMIT 10;
        """, discord_id)
        return pvm_records

    async def get_pvm_points(self, discord_id):
        return await self.pool.fetchval("""
        SELECT pvm_points FROM users
        WHERE discord_id = $1;
        """, discord_id)

    async def get_warn_points(self, discord_id):
        return await self.pool.fetchval("""
        SELECT warn_points FROM users
        WHERE discord_id =$1
        """, discord_id)

    async def insert_alts(self, discord_id, *alts):
        return await self.pool.fetchval("""
        UPDATE users
        SET alt_names = $1
        WHERE discord_id = $2
        RETURNING alt_names;
        """, alts, discord_id)


