import datetime as dt
import os
import textwrap

import pytest
import systemd.journal


@pytest.fixture
def client(request, cursor):
    from jd2cw import CloudWatchClient

    client = CloudWatchClient(request.fixturename, cursor, 1, {})
    return client


@pytest.fixture
def now():
    return dt.datetime.now()


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


@pytest.fixture(scope="session")
def setup_env():
    os.environ["AWS_ACCESS_KEY_ID"] = "testtest"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testtest"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
