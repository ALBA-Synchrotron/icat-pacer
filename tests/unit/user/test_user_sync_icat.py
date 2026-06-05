from helpers.contexts.user import create_user_context


class TestICATUserSync:

    def test_create_user_icat(self, user_tasks, icat_client, valid_user):
        user_ctx = create_user_context(valid_user)

        users = icat_client.search("User", conditions={"email__eq": user_ctx.email}, flatten_single=False)
        assert len(users) == 0

        user_tasks.sync_user_icat(icat_client, user_ctx)

        users = icat_client.search("User", conditions={"email__eq": user_ctx.email}, flatten_single=False)
        assert len(users) == 3

    def test_update_user_icat(self, user_tasks, icat_client, valid_user):
        user_ctx = create_user_context(valid_user)
        user_tasks.sync_user_icat(icat_client, user_ctx)

        users = icat_client.search("User", conditions={"email__eq": user_ctx.email}, flatten_single=False)
        assert len(users) == 3

        user_ctx.first_name = "updated"
        user_tasks.sync_user_icat(icat_client, user_ctx)

        users = icat_client.search("User", conditions={"email__eq": user_ctx.email}, flatten_single=False)
        assert len(users) == 3
        assert all(user_ctx.first_name == user.givenName for user in users)
        assert all(user.name == user.name.lower() for user in users)

    def test_disable_user_icat(self, user_tasks, icat_client, valid_user):
        user_ctx = create_user_context(valid_user)
        user_tasks.sync_user_icat(icat_client, user_ctx)

        users = icat_client.search("User", conditions={"email__eq": user_ctx.email}, flatten_single=False)
        assert len(users) == 3

        user_ctx.enabled = False
        user_tasks.sync_user_icat(icat_client, user_ctx)

        users = icat_client.search("User", conditions={"email__eq": user_ctx.email}, flatten_single=False)
        assert len(users) == 3
        assert all(user.name.endswith("__user_disabled") for user in users)

    def test_enable_user_icat(self, user_tasks, icat_client, valid_user):
        user_ctx = create_user_context(valid_user)
        user_ctx.enabled = False
        user_tasks.sync_user_icat(icat_client, user_ctx)

        users = icat_client.search("User", conditions={"email__eq": user_ctx.email}, flatten_single=False)
        assert len(users) == 3

        user_ctx.enabled = True
        user_tasks.sync_user_icat(icat_client, user_ctx)

        users = icat_client.search("User", conditions={"email__eq": user_ctx.email}, flatten_single=False)
        assert len(users) == 3
        assert all(user.name.endswith("__user_disabled") for user in users) == False