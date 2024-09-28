"""
    :codeauthor: Rupesh Tare <rupesht@saltstack.com>
"""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import saltext.influxdb.modules.influxdb08mod as influx08

DB_LIST = ["A", "B", "C"]
USER_LIST = [{"name": "A"}, {"name": "B"}]


class MockInfluxDBClient:
    def get_list_database(self):
        return DB_LIST

    def create_database(self, name):
        return name

    def delete_database(self, name):
        return name

    def switch_database(self, name):
        return name

    def get_list_users(self):
        return USER_LIST

    def get_list_cluster_admins(self):
        return USER_LIST

    def update_cluster_admin_password(self, name, passwd):
        return name, passwd

    def update_database_user_password(self, name, passwd):
        return name, passwd

    def delete_cluster_admin(self, name):
        return name

    def delete_database_user(self, name):
        return name

    def query(self, query, time_precision, chunked):
        return query, time_precision, chunked


@pytest.fixture
def client():
    _client = MockInfluxDBClient()
    with patch.object(influx08, "_client", MagicMock(return_value=_client)):
        yield _client


@pytest.mark.usefixtures("client")
def test_db_list():
    """
    Test to list all InfluxDB databases
    """
    assert influx08.db_list(user="root", password="root", host="localhost", port=8086) == DB_LIST


def test_db_exists():
    """
    Tests for checks if a database exists in InfluxDB
    """
    with patch.object(influx08, "db_list", side_effect=[[{"name": "A"}], None]):
        assert influx08.db_exists(
            name="A", user="root", password="root", host="localhost", port=8000
        )

        assert not influx08.db_exists(
            name="A", user="root", password="root", host="localhost", port=8000
        )


@pytest.mark.usefixtures("client")
@pytest.mark.parametrize("exists", (True, False))
def test_db_create(exists):
    """
    Test to create a database
    """
    with patch.object(influx08, "db_exists", return_value=exists):
        assert (
            influx08.db_create(name="A", user="root", password="root", host="localhost", port=8000)
            is not exists
        )


@pytest.mark.usefixtures("client")
@pytest.mark.parametrize("exists", (True, False))
def test_db_remove(exists):
    """
    Test to remove a database
    """
    with patch.object(influx08, "db_exists", return_value=exists):
        assert (
            bool(
                influx08.db_remove(
                    name="A", user="root", password="root", host="localhost", port=8000
                )
            )
            is exists
        )


@pytest.mark.usefixtures("client")
def test_user_list():
    """
    Tests  for list cluster admins or database users.
    """
    assert (
        influx08.user_list(
            database="A",
            user="root",
            password="root",
            host="localhost",
            port=8086,
        )
        == USER_LIST
    )

    assert (
        influx08.user_list(user="root", password="root", host="localhost", port=8086) == USER_LIST
    )


def test_user_exists():
    """
    Test to checks if a cluster admin or database user exists.
    """
    with patch.object(influx08, "user_list", side_effect=[[{"name": "A"}], None]):
        assert influx08.user_exists(
            name="A", user="root", password="root", host="localhost", port=8000
        )

        assert not influx08.user_exists(
            name="A", user="root", password="root", host="localhost", port=8000
        )


@pytest.mark.usefixtures("client")
def test_user_chpass():
    """
    Tests to change password for a cluster admin or a database user.
    """
    with patch.object(influx08, "user_exists", return_value=False):
        assert not influx08.user_chpass(
            name="A",
            passwd="*",
            user="root",
            password="root",
            host="localhost",
            port=8000,
        )

        assert not influx08.user_chpass(
            name="A",
            passwd="*",
            database="test",
            user="root",
            password="root",
            host="localhost",
            port=8000,
        )

    with patch.object(influx08, "user_exists", return_value=True):
        assert influx08.user_chpass(
            name="A",
            passwd="*",
            user="root",
            password="root",
            host="localhost",
            port=8000,
        )

        assert influx08.user_chpass(
            name="A",
            passwd="*",
            database="test",
            user="root",
            password="root",
            host="localhost",
            port=8000,
        )


@pytest.mark.usefixtures("client")
def test_user_remove():
    """
    Tests to remove a cluster admin or a database user.
    """
    with patch.object(influx08, "user_exists", return_value=False):
        assert not influx08.user_remove(
            name="A", user="root", password="root", host="localhost", port=8000
        )

        assert not influx08.user_remove(
            name="A",
            database="test",
            user="root",
            password="root",
            host="localhost",
            port=8000,
        )

    with patch.object(influx08, "user_exists", return_value=True):
        assert influx08.user_remove(
            name="A",
            user="root",
            password="root",
            host="localhost",
            port=8000,
        )

        assert influx08.user_remove(
            name="A",
            database="test",
            user="root",
            password="root",
            host="localhost",
            port=8000,
        )


@pytest.mark.usefixtures("client")
def test_query():
    """
    Test for querying data
    """
    assert influx08.query(
        database="db",
        query="q",
        user="root",
        password="root",
        host="localhost",
        port=8000,
    )


def test_retention_policy_get(client):
    policy = {"name": "foo"}
    client.get_list_retention_policies = MagicMock(return_value=[policy])
    assert policy == influx08.retention_policy_get(database="db", name="foo")


def test_retention_policy_add(client):
    client.create_retention_policy = MagicMock()
    assert influx08.retention_policy_add(
        database="db",
        name="name",
        duration="30d",
        replication=1,
    )
    client.create_retention_policy.assert_called_once_with("name", "30d", 1, "db", False)


def test_retention_policy_modify(client):
    client.alter_retention_policy = MagicMock()
    assert influx08.retention_policy_alter(
        database="db",
        name="name",
        duration="30d",
        replication=1,
    )
    client.alter_retention_policy.assert_called_once_with("name", "db", "30d", 1, False)
