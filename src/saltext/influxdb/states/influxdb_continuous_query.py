"""
Manage InfluxDB 0.9-1.x continuous queries statefully.

.. important::
    You can optionally specify default connection parameters via the general :ref:`influxdb setup <influxdb-setup>`.
"""


def __virtual__():
    if "influxdb.db_exists" in __salt__:
        return "influxdb_continuous_query"
    return (False, "influxdb module could not be loaded")


def present(name, database, query, resample_time=None, coverage_period=None, **client_args):
    """
    Ensure that given continuous query is present.

    name
        Name of the continuous query to create.

    database
        Database to create continuous query on.

    query
        The query content

    resample_time : None
        Duration between continuous query resampling.

    coverage_period : None
        Duration specifying time period per sample.
    """
    ret = {
        "name": name,
        "changes": {},
        "result": True,
        "comment": f"continuous query {name} is already present",
    }

    if not __salt__["influxdb.continuous_query_exists"](
        name=name, database=database, **client_args
    ):
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f" {name} is absent and will be created"
            return ret
        if __salt__["influxdb.create_continuous_query"](
            database, name, query, resample_time, coverage_period, **client_args
        ):
            ret["comment"] = f"continuous query {name} has been created"
            ret["changes"][name] = "Present"
            return ret
        else:
            ret["comment"] = f"Failed to create continuous query {name}"
            ret["result"] = False
            return ret

    return ret


def absent(name, database, **client_args):
    """
    Ensure that given continuous query is absent.

    name
        Name of the continuous query to remove.

    database
        Name of the database that the continuous query was defined on.
    """
    ret = {
        "name": name,
        "changes": {},
        "result": True,
        "comment": f"continuous query {name} is not present",
    }

    if __salt__["influxdb.continuous_query_exists"](database, name, **client_args):
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"continuous query {name} is present and needs to be removed"
            return ret
        if __salt__["influxdb.drop_continuous_query"](database, name, **client_args):
            ret["comment"] = f"continuous query {name} has been removed"
            ret["changes"][name] = "Absent"
            return ret
        else:
            ret["comment"] = f"Failed to remove continuous query {name}"
            ret["result"] = False
            return ret

    return ret
