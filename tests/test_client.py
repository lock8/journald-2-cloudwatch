import datetime as dt
import json
import os
import uuid

import pytest
from moto import mock_aws


def test_client_make_message(client, now):
    uuid_ = uuid.uuid4()
    encoded = client.make_message({
        "__REALTIME_TIMESTAMP": now,
        "float": .1,
        "str": "",
        "bytes": b"",
        "int": 1,
        "uuid": uuid_,
        "datetime": now})

    assert json.loads(encoded["message"]) == {
        "__REALTIME_TIMESTAMP": now.timestamp(),
        "float": .1,
        "str": "",
        "bytes": "",
        "int": 1,
        "uuid": str(uuid_),
        "datetime": now.timestamp(),
    }


@mock_aws
def test_client_create_log_group(client, setup_env):
    client.create_log_group()


def test_client_log_messages_error_if_not_configured(client):
    with pytest.raises(RuntimeError):
        client.log_messages("stream", [])


@mock_aws
def test_client_log_messages(client, now, setup_env):
    client.configure()
    first_ts = now
    second_ts = now - dt.timedelta(seconds=1)
    client.log_messages("stream", [
        {
            "MESSAGE": "message1",
            "__REALTIME_TIMESTAMP": first_ts,
            "__CURSOR": "cur1",
        },
        {
            "MESSAGE": "message2",
            "__REALTIME_TIMESTAMP": second_ts,
            "__CURSOR": "cur2",
        },
    ])

    with open(client.cursor_path) as c_file:
        assert c_file.read() == "cur2"


def test_client_group_messages(client, now):
    messages = []
    for x in range(11):
        messages.append({"__REALTIME_TIMESTAMP": now})
    x = len(list(client.group_messages(messages, 2, dt.timedelta(hours=12))))
    assert x == 6
    ts_1 = now
    ts_2 = now + dt.timedelta(hours=24)
    ts_3 = now - dt.timedelta(hours=24)
    messages = [
        {"__REALTIME_TIMESTAMP": ts_1, },
        {"__REALTIME_TIMESTAMP": ts_2, },
        {"__REALTIME_TIMESTAMP": ts_3, },
    ]
    x = len(list(client.group_messages(messages, 3, dt.timedelta(hours=23))))
    assert x == 3
