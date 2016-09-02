import datetime as dt
import textwrap


import botocore.vendored.requests
import pytest
import requests_mock
import requests_mock.mocker
import systemd.journal


@pytest.fixture
def client(request, cursor):
    from jd2cw import CloudWatchClient

    with requests_mock.mock() as m:
        m.post('https://logs.eu-west-1.amazonaws.com/')
        m.get('http://169.254.169.254/latest/meta-data/iam/'
              'security-credentials/')
        client = CloudWatchClient(request.fixturename, cursor, 1)
    return client


@pytest.fixture
def now():
    return dt.datetime.now()


@pytest.fixture(autouse=True, scope='session')
def mock_vendored_requests():
    requests_mock.mocker.requests = botocore.vendored.requests


@pytest.fixture
def cursor(tmpdir_factory):
    cursor = tmpdir_factory.mktemp('tmp').join('cursor')
    return cursor.strpath


@pytest.fixture
def journal_dir(tmpdir_factory):
    journal_dir = tmpdir_factory.mktemp('journal')
    return journal_dir.strpath


@pytest.fixture(autouse=True, scope='session')
def command():
    def wait(*args):
        raise KeyboardInterrupt

    systemd.journal.Reader.wait = wait


@pytest.fixture
def config_file(tmpdir_factory, cursor, journal_dir):
    config = textwrap.dedent("""
    [jd2cw]
    log-group = foo
    cursor = {}
    logs = {}
    retention = 10
    """.format(cursor, journal_dir))
    fn = tmpdir_factory.mktemp('config').join('config.ini')
    with open(fn.strpath, 'w') as open_file:
        open_file.write(config)

    return fn.strpath
