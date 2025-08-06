import datetime
from logging import Logger
from psycopg_pool import ConnectionPool

from helpers.common import get_affiliation_name
from helpers.dataclasses import InvestigationContext
from helpers.user import UserContext, Affiliation


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
    def db_update_investigation_doi(cls, pool: ConnectionPool, investigation: str, doi: str, doi_landing_url: str,
                                    logger: Logger) -> None:
        query: str = """UPDATE experiment
                        SET doi=%s,
                            url=%s
                        WHERE id = %s"""
        logger.debug(
            f"Writing to VISA db an investigation DOI update: investigation={investigation} doi={doi} url={doi_landing_url}")
        params: tuple = (doi, doi_landing_url, investigation)
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
        except Exception as e:
            error_msg: str = f"Error updating investigation's DOI / DOI url to VISA db (db_table=experiment): {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
        query: str = """UPDATE proposal
                        SET doi=%s,
                            url=%s
                        WHERE id = %s"""
        logger.debug(
            f"Writing to VISA db an investigation DOI update: investigation={investigation} doi={doi} url={doi_landing_url}")
        params: tuple = (doi, doi_landing_url, investigation)
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
        except Exception as e:
            error_msg: str = f"Error updating investigation's DOI / DOI url to VISA db (db_table=proposal): {e}"
            logger.error(error_msg)
            raise Exception(error_msg)

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
            error_msg: str = f"Error writing affiliation / employer to VISA db: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)

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
                    error_msg: str = f"Error writing user to VISA db: {e}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                match user_ctx.is_staff:
                    case True:
                        staff_id: int = -1
                        query: str = "SELECT id FROM role WHERE name = 'STAFF'"
                        try:
                            cur.execute(query)
                            res = cur.fetchone()
                            staff_id: int = res[0] if res else 1
                        except Exception as e:
                            error_msg: str = f"Error fetching staff role_id from visa db: {e}"
                            logger.error(error_msg)
                            raise Exception(error_msg)

                        if staff_id:
                            logger.debug(f"Writing to VISA db: Adding  STAFF role to user profile_id={user_ctx.uos_id}")
                            query: str = """INSERT INTO user_role (user_id, role_id)
                                            VALUES (%s, %s) ON CONFLICT DO NOTHING"""
                            params: tuple = (user_ctx.uos_id,
                                             staff_id)
                            try:
                                cur.execute(query, params)
                            except Exception as e:
                                error_msg: str = f"Error writing STAFF role to user profile_id={user_ctx.uos_id} to visa db: {e}"
                                logger.error(error_msg)
                                raise Exception(error_msg)

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
                            error_msg: str = f"Error deleting STAFF role from user profile_id={user_ctx.uos_id} to visa db: {e}"
                            logger.error(error_msg)
                            raise Exception(error_msg)

    @classmethod
    def db_sync_proposal(cls, pool: ConnectionPool, investigation_context: InvestigationContext, logger: Logger):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                query: str = """
                        INSERT INTO proposal (id, identifier, title, doi, url, summary, public_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO
                        UPDATE
                            SET identifier = %s, title = %s, doi = %s, url = %s, summary = %s, public_at = %s
                    """
                params: tuple = (
                    int(investigation_context.name),
                    investigation_context.name,
                    investigation_context.title,
                    investigation_context.doi,
                    investigation_context.url,
                    investigation_context.summary,
                    investigation_context.release_date,
                    investigation_context.name,
                    investigation_context.title,
                    investigation_context.doi,
                    investigation_context.url,
                    investigation_context.summary,
                    investigation_context.release_date
                )
                try:
                    cur.execute(query, params)
                except Exception as e:
                    logger.error(f"Error synchronizing Proposal {investigation_context.name} to visa db: {e}")

    @classmethod
    def db_sync_experiment(cls, pool: ConnectionPool, investigation_context: InvestigationContext, logger: Logger):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                query: str = "select id from instrument where name LIKE %s"
                params: tuple = (investigation_context.instrument.get('name'),)
                cur.execute(query, params)
                res = cur.fetchone()
                instrument_id = res[0] if res else 1

                insert_query: str = """
                        INSERT INTO experiment (id, proposal_id, instrument_id, start_date, end_date, title, url, doi)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO 
                        UPDATE
                            SET proposal_id=%s, instrument_id=%s, start_date=%s, end_date=%s, title=%s, url=%s, doi=%s
                    """
                insert_params: tuple = (
                    investigation_context.name,
                    int(investigation_context.name),
                    int(instrument_id),
                    investigation_context.start_date,
                    investigation_context.end_date,
                    investigation_context.title,
                    investigation_context.url,
                    investigation_context.doi,
                    int(investigation_context.name),
                    int(instrument_id),
                    investigation_context.start_date,
                    investigation_context.end_date,
                    investigation_context.title,
                    investigation_context.url,
                    investigation_context.doi
                )
                try:
                    cur.execute(insert_query, insert_params)
                except Exception as e:
                    logger.error(f"Error synchronizing Experiment {investigation_context.name} to visa db: {e}")

    @classmethod
    def db_sync_experiment_user(cls, pool: ConnectionPool, investigation_context: InvestigationContext, logger: Logger):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                for ctx_user in investigation_context.user_list:
                    query: str = "select id from users where email = %s"
                    params: tuple = (ctx_user['email'],)
                    cur.execute(query, params)
                    res = cur.fetchone()
                    user_id = res[0] if res else 1
                    insert_query: str = """
                            INSERT INTO experiment_user (experiment_id, user_id)
                            VALUES (%s, %s) ON CONFLICT DO NOTHING
                        """
                    insert_params: tuple = (
                        int(investigation_context.name),
                        user_id
                    )
                    try:
                        cur.execute(insert_query, insert_params)
                    except Exception as e:
                        logger.error(
                            f"Error synchronizing Experiment User {ctx_user['email']} for {investigation_context.name} to visa db: {e}")
