"""
Manage InfluxDB 0.5-0.8 databases statefully.

.. important::
    You can optionally specify default connection parameters via the general :ref:`influxdb08 setup <influxdb08-setup>`.
"""


def __virtual__():
    if "influxdb08.db_exists" in __salt__:
        return "influxdb08_database"
    return (False, "influxdb08 module could not be loaded")


def present(name, user=None, password=None, host=None, port=None):
    """
    Ensure that the named database is present

    name
        The name of the database to create

    user
        The user to connect as (must be able to remove the database)

    password
        The password of the user

    host
        The host to connect to

    port
        The port to connect to

    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    # check if database exists
    if not __salt__["influxdb08.db_exists"](name, user, password, host, port):
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"Database {name} is absent and needs to be created"
            return ret
        if __salt__["influxdb08.db_create"](name, user, password, host, port):
            ret["comment"] = f"Database {name} has been created"
            ret["changes"][name] = "Present"
            return ret
        else:
            ret["comment"] = f"Failed to create database {name}"
            ret["result"] = False
            return ret

    # fallback
    ret["comment"] = f"Database {name} is already present, so cannot be created"
    return ret


def absent(name, user=None, password=None, host=None, port=None):
    """
    Ensure that the named database is absent

    name
        The name of the database to remove

    user
        The user to connect as (must be able to remove the database)

    password
        The password of the user

    host
        The host to connect to

    port
        The port to connect to

    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    # check if database exists and remove it
    if __salt__["influxdb08.db_exists"](name, user, password, host, port):
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"Database {name} is present and needs to be removed"
            return ret
        if __salt__["influxdb08.db_remove"](name, user, password, host, port):
            ret["comment"] = f"Database {name} has been removed"
            ret["changes"][name] = "Absent"
            return ret
        else:
            ret["comment"] = f"Failed to remove database {name}"
            ret["result"] = False
            return ret

    # fallback
    ret["comment"] = f"Database {name} is not present, so it cannot be removed"
    return ret
