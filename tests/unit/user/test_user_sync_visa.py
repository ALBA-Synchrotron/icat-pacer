from helpers.contexts.user import create_user_context


class TestVISAUSerSync:

    def test_visa_user_sync(self, user_tasks, mock_psycopg_pool, valid_user):
        user_ctx = create_user_context(valid_user)

        user_tasks.sync_user_visa(mock_psycopg_pool, user_ctx)
        calls: list = mock_psycopg_pool.connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.call_args_list
        sql_statements: list = [call.args[0] for call in calls]

        has_insert = any("INSERT" in sql.upper() for sql in sql_statements)
        assert has_insert, "No INSERT statements executed"
