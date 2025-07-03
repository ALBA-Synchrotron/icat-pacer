import datetime
from logging import Logger
from psycopg_pool import ConnectionPool

from helpers.user import UserContext, get_affiliation_name, Affiliation


def get_pg_connection_pool(config: dict) -> ConnectionPool:
    visa_config: dict = config.get("integrations", {}).get("visa", {})

    enabled: bool = visa_config.get("enabled", False)
    if not enabled:
        raise Exception("visa integration is not enabled")

    visa_db_config: dict = visa_config.get("database", {})
    host: str = visa_db_config.get("host", "")
    port: int = visa_db_config.get("port", 5432)
    user: str = visa_db_config.get("username", "")
    password: str = visa_db_config.get("password", "")
    database: str = visa_db_config.get("database", "")

    visa_dsn: str = f"host={host} port={port} user={user} password={password} dbname={database}"

    return ConnectionPool(conninfo=visa_dsn, max_size=6)


class VISALoader:

    @classmethod
    def db_sync_affiliation(cls, pool: ConnectionPool, affiliation: Affiliation, logger: Logger) -> None:
        query: str = """INSERT INTO employer (id, name, town, country_code)
                        VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO
        UPDATE
            SET name = %s, town = %s, country_code = %s"""
        logger.debug(
            f"Writing to VISA db affiliation / employer: id={affiliation.id} name={affiliation.name} city={affiliation.city} country={affiliation.country_code}")
        params: tuple = (affiliation.id,
                         get_affiliation_name(affiliation=affiliation, limit=200),
                         affiliation.city,
                         affiliation.country_code,
                         get_affiliation_name(affiliation=affiliation, limit=200),
                         affiliation.city,
                         affiliation.country_code)
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
        except Exception as e:
            logger.error(f"Error writing affiliation / employer to VISA db: {e}")

    @classmethod
    def db_sync_user(cls, pool: ConnectionPool, user_ctx: UserContext, logger: Logger) -> None:
        min_date: str = "1970-05-15 09:00:43.516"
        now_date: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        query: str = f"""INSERT INTO users (id, first_name, last_name, email, affiliation_id, instance_quota, activated_at,
                                      last_seen_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO
                UPDATE
                    SET first_name = %s, last_name = %s, email = %s, affiliation_id = %s {", instance_quota = 0" if not user_ctx.enabled else ""}"""

        logger.debug(f"Writing to VISA db user: profile_id={user_ctx.uos_id}")
        params: tuple = (str(user_ctx.uos_id),
                         user_ctx.first_name,
                         user_ctx.last_name,
                         user_ctx.email,
                         int(user_ctx.affiliation.id),
                         0,
                         now_date,
                         min_date,
                         user_ctx.first_name,
                         user_ctx.last_name,
                         user_ctx.email,
                         int(user_ctx.affiliation.id),
                         )

        with pool.connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(query, params)
                except Exception as e:
                    logger.error(f"Error writing user to VISA db: {e}")

                match user_ctx.is_staff:
                    case True:
                        staff_id: int = -1
                        query: str = "SELECT id FROM role WHERE name = 'STAFF'"
                        try:
                            cur.execute(query)
                            res = cur.fetchone()
                            staff_id: int = res[0] if res else 1
                        except Exception as e:
                            logger.error(f"Error fetching staff role_id from visa db: {e}")

                        if staff_id:
                            logger.debug(f"Writing to VISA db: Adding  STAFF role to user profile_id={user_ctx.uos_id}")
                            query: str = """INSERT INTO user_role (user_id, role_id)
                                            VALUES (%s, %s) ON CONFLICT DO NOTHING"""
                            params: tuple = (user_ctx.uos_id,
                                             staff_id)
                            try:
                                cur.execute(query, params)
                            except Exception as e:
                                logger.error(
                                    f"Error writing STAFF role to user profile_id={user_ctx.uos_id} to visa db: {e}")

                    case False:
                        logger.debug(
                            f"Deleting from VISA db: Removing STAFF role from user profile_id={user_ctx.uos_id}")
                        query: str = """DELETE
                                        FROM user_role
                                        WHERE user_id = %s"""
                        params: tuple = (str(user_ctx.uos_id),)
                        try:
                            cur.execute(query, params)
                        except Exception as e:
                            logger.error(
                                f"Error deleting STAFF role from user profile_id={user_ctx.uos_id} to visa db: {e}")
                # TODO: Fix up these functions below when proposal sync is implemented. Change func names and attributes to match
                #       those defined above for user and affiliation sync.
            """
            @classmethod
            async def db_sync_experiment(cls, experiments):
                async with conn.transaction():
                    inserted = 0
                    updated = 0
                    total_lines = 0
                    for experiment in experiments:
                        instrument_id = await conn.fetchval(
                            "select id from instrument where name LIKE '{}%'".format(experiment['instrument']))
            
                        res = await conn.execute(
                            \"""INSERT INTO experiment (id, proposal_id, instrument_id, start_date, end_date, title, url, doi)
                               VALUES ($1, $2, $3, $4, $5, $6, $7, $8) ON CONFLICT (id) DO
                            UPDATE
                                SET proposal_id = $2, instrument_id=$3, start_date=$4, end_date=$5, title=$6, url=$7, doi=$8\""",
                            experiment['id'],
                            int(experiment['proposal_id']),
                            instrument_id,
                            experiment['start_date'],
                            experiment['end_date'],
                            experiment['title'],
                            experiment['url'],
                            experiment['doi']
                        )
                        response_parsed = self.parse_response_reg.match(res)
                        inserted += int(response_parsed.group(1))
                        updated += int(response_parsed.group(2))
                        total_lines += 1
                    print("Experiment : INSERT {0} UPDATE {1} TOTAL {2}".format(inserted, updated, total_lines))
            
            async def experiment_user(self, exp_users):
                async with self.conn.transaction():
                    inserted = 0
                    updated = 0
                    total_lines = 0
                    for exp_user in exp_users:
                        user_id = await self.conn.fetchval(
                            "select id from users where email = '{}'".format(exp_user['email']))
                        if user_id:
                            res = await self.conn.execute(
                                \"""INSERT INTO experiment_user (experiment_id, user_id)
                                   VALUES ($1, $2) ON CONFLICT DO NOTHING\""",
                                exp_user['experiment_id'],
                                user_id)
                            response_parsed = self.parse_response_reg.match(res)
                            inserted += int(response_parsed.group(1))
                            updated += int(response_parsed.group(2))
                            total_lines += 1
                    print("Experiment User : INSERT {0} UPDATE {1} TOTAL {2}".format(inserted, updated, total_lines))
            
            async def instrument_control_user(self, ic_users):
                async with self.conn.transaction():
                    inserted = 0
                    updated = 0
                    total_lines = 0
            
                    instrument_control_id = await self.conn.fetchval("select id from role where name = 'INSTRUMENT_CONTROL'")
                    for ic_user in ic_users:
                        res = await self.conn.execute(
                            \"""INSERT INTO user_role (user_id, role_id)
                               VALUES ($1, $2) ON CONFLICT DO NOTHING\""",
                            ic_user['user_id'],
                            instrument_control_id)
                        response_parsed = self.parse_response_reg.match(res)
                        inserted += int(response_parsed.group(1))
                        updated += int(response_parsed.group(2))
                        total_lines += 1
                    print("Instrument Control User : INSERT {0} UPDATE {1} TOTAL {2}".format(inserted, updated, total_lines))
            
            async def instrument(self, instruments):
                async with self.conn.transaction():
                    inserted = 0
                    updated = 0
                    total_lines = 0
                    for instrument in instruments:
                        res = await self.conn.execute(
                            \"""INSERT INTO instrument (id, name)
                               VALUES ($1, $2) ON CONFLICT (id) DO
                            UPDATE
                                SET name = $2\""",
                            int(instrument['id']),
                            instrument['name']
                        )
                        response_parsed = self.parse_response_reg.match(res)
                        inserted += int(response_parsed.group(1))
                        updated += int(response_parsed.group(2))
                        total_lines += 1
                    print("Instrument : INSERT {0} UPDATE {1} TOTAL {2}".format(inserted, updated, total_lines))
            
            async def instrument_scientist(self, instrument_scientists):
                async with self.conn.transaction():
                    inserted = 0
                    updated = 0
                    total_lines = 0
                    for instrument_scientist in instrument_scientists:
                        res = await self.conn.execute(
                            \"""INSERT INTO instrument_scientist (instrument_id, user_id)
                               VALUES ($1, $2) ON CONFLICT DO NOTHING\""",
                            int(instrument_scientist['instrument_id']),
                            instrument_scientist['user_id']
                        )
                        response_parsed = self.parse_response_reg.match(res)
                        inserted += int(response_parsed.group(1))
                        updated += int(response_parsed.group(2))
                        total_lines += 1
                    print("Instrument responsible : INSERT {0} UPDATE {1} TOTAL {2}".format(inserted, updated, total_lines))
            
            async def proposal(self, proposals):
                async with self.conn.transaction():
                    inserted = 0
                    updated = 0
                    total_lines = 0
                    for proposal in proposals:
                        res = await self.conn.execute(
                            \"""INSERT INTO proposal (id, identifier, title, doi, url, summary, public_at)
                               VALUES ($1, $2, $3, $4, $5, $6, $7) ON CONFLICT (id) DO
                            UPDATE
                                SET identifier = $2, title = $3, doi = $4, url = $5, summary = $6, public_at = $7\""",
                            int(proposal['id']),
                            proposal['identifier'],
                            proposal['title'],
                            proposal['doi'],
                            proposal['url'],
                            proposal['summary'],
                            proposal['public_at']
                        )
                        response_parsed = self.parse_response_reg.match(res)
                        inserted += int(response_parsed.group(1))
                        updated += int(response_parsed.group(2))
                        total_lines += 1
                    print("Proposal : INSERT {0} UPDATE {1} TOTAL {2}".format(inserted, updated, total_lines))
            """
