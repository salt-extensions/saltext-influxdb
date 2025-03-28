"""
:codeauthor: Jayesh Kariya <jayeshk@saltstack.com>
"""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from saltext.influxdb.states import influxdb08_user


@pytest.fixture
def configure_loader_modules():
    return {influxdb08_user: {}}


def test_present():
    """
    Test to ensure that the cluster admin or database user is present.
    """
    name = "salt"
    passwd = "salt"

    ret = {"name": name, "result": False, "comment": "", "changes": {}}

    mock = MagicMock(side_effect=[False, False, False, True])
    mock_t = MagicMock(side_effect=[True, False])
    mock_f = MagicMock(return_value=False)
    with patch.dict(
        influxdb08_user.__salt__,
        {
            "influxdb08.db_exists": mock_f,
            "influxdb08.user_exists": mock,
            "influxdb08.user_create": mock_t,
        },
    ):
        comt = "Database mydb does not exist"
        ret.update({"comment": comt})
        assert influxdb08_user.present(name, passwd, database="mydb") == ret

        with patch.dict(influxdb08_user.__opts__, {"test": True}):
            comt = f"User {name} is not present and needs to be created"
            ret.update({"comment": comt, "result": None})
            assert influxdb08_user.present(name, passwd) == ret

        with patch.dict(influxdb08_user.__opts__, {"test": False}):
            comt = f"User {name} has been created"
            ret.update({"comment": comt, "result": True, "changes": {"salt": "Present"}})
            assert influxdb08_user.present(name, passwd) == ret

            comt = f"Failed to create user {name}"
            ret.update({"comment": comt, "result": False, "changes": {}})
            assert influxdb08_user.present(name, passwd) == ret

        comt = f"User {name} is already present"
        ret.update({"comment": comt, "result": True})
        assert influxdb08_user.present(name, passwd) == ret


def test_absent():
    """
    Test to ensure that the named cluster admin or database user is absent.
    """
    name = "salt"

    ret = {"name": name, "result": None, "comment": "", "changes": {}}

    mock = MagicMock(side_effect=[True, True, True, False])
    mock_t = MagicMock(side_effect=[True, False])
    with patch.dict(
        influxdb08_user.__salt__,
        {"influxdb08.user_exists": mock, "influxdb08.user_remove": mock_t},
    ):
        with patch.dict(influxdb08_user.__opts__, {"test": True}):
            comt = f"User {name} is present and needs to be removed"
            ret.update({"comment": comt})
            assert influxdb08_user.absent(name) == ret

        with patch.dict(influxdb08_user.__opts__, {"test": False}):
            comt = f"User {name} has been removed"
            ret.update({"comment": comt, "result": True, "changes": {"salt": "Absent"}})
            assert influxdb08_user.absent(name) == ret

            comt = f"Failed to remove user {name}"
            ret.update({"comment": comt, "result": False, "changes": {}})
            assert influxdb08_user.absent(name) == ret

        comt = f"User {name} is not present, so it cannot be removed"
        ret.update({"comment": comt, "result": True})
        assert influxdb08_user.absent(name) == ret
