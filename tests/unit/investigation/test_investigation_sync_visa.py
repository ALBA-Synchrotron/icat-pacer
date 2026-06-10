from helpers.contexts.investigation import create_investigation_context


class TestVISAInvestigationSync:

    def test_visa_investigation_sync(self, investigation_tasks, mock_psycopg_pool, valid_investigation):
        inv_ctx = create_investigation_context(valid_investigation)
        investigation_tasks.sync_investigation_visa(mock_psycopg_pool, inv_ctx)

        calls: list = mock_psycopg_pool.connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.call_args_list
        sql_statements: list = [call.args[0] for call in calls]

        has_insert = any("INSERT" in sql.upper() for sql in sql_statements)
        assert has_insert, "No INSERT statements executed"
