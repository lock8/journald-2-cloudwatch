import datetime as dt
import json
import urllib.parse
import uuid

import pytest
import requests_mock


def test_client_make_message(client, now):
    uuid_ = uuid.uuid4()
    encoded = client.make_message({
        '__REALTIME_TIMESTAMP': now,
        'float': .1,
        'str': '',
        'bytes': b'',
        'int': 1,
        'uuid': uuid_,
        'datetime': now})

    assert json.loads(encoded['message']) == {
        '__REALTIME_TIMESTAMP': now.timestamp(),
        'float': .1,
        'str': '',
        'bytes': '',
        'int': 1,
        'uuid': str(uuid_),
        'datetime': now.timestamp(),
    }


def test_client_create_log_group(client):
    with requests_mock.mock() as m:
        m.post('https://logs.eu-west-1.amazonaws.com/')
        client.create_log_group()
    assert m.call_count == 2


def test_client_create_log_group_and_sub(client):
    destination_arn = 'arn:aws:lambda:eu-west-1:XXX:function:sub'
    client.subscription_filter_config = {
        'destinationArn': destination_arn,
        'filterName': 'push_to_lambda',
        'filterPattern': '',
        'logGroupName': client.log_group,
    }
    with requests_mock.mock() as m:
        m.post('https://logs.eu-west-1.amazonaws.com/')
        m.post('https://lambda.eu-west-1.amazonaws.com/2015-03-31/functions/'
               '{}/policy'.format(urllib.parse.quote(destination_arn)))
        client.create_log_group()
    assert m.call_count == 4


def test_client_log_stream(client):
    with requests_mock.mock() as m:
        m.post('https://logs.eu-west-1.amazonaws.com/')
        client.create_log_stream('stream')
    assert m.called


def test_client_log_messages_error_if_not_configured(client):
    with pytest.raises(RuntimeError):
        client.log_messages('stream', [])


def test_client_log_messages(client, now):
    with requests_mock.mock() as m:
        m.post('https://logs.eu-west-1.amazonaws.com/')
        client.configure()

    def callback(request, context):
        print(request, context)
        return ''

    with requests_mock.mock() as m:
        m.post('https://logs.eu-west-1.amazonaws.com/', [
            {'json': {
                'logStreams': [
                    {
                        'arn': 'arn:stream',
                        'creationTime': now.timestamp(),
                        'firstEventTimestamp': now.timestamp(),
                        'lastEventTimestamp': now.timestamp(),
                        'lastIngestionTime': now.timestamp(),
                        'logStreamName': 'stream',
                        'storedBytes': 0,
                        'uploadSequenceToken': 'abcd'
                    }
                ],
                'nextToken': 'abcde'},
             'status_code': 200,
             },
            {'json': {'nextSequenceToken': 'abcd'}},
        ])
        first_ts = now
        second_ts = now - dt.timedelta(seconds=1)
        client.log_messages('stream', [
            {'MESSAGE': 'message1',
             '__REALTIME_TIMESTAMP': first_ts,
             '__CURSOR': 'cur1',
             },
            {'MESSAGE': 'message2',
             '__REALTIME_TIMESTAMP': second_ts,
             '__CURSOR': 'cur2',
             },
        ])
    assert m.call_count == 2
    assert [e['timestamp']
            for e in m.request_history[1].json()['logEvents']] == [
                    int(second_ts.timestamp() * 1000),
                    int(first_ts.timestamp() * 1000)]
