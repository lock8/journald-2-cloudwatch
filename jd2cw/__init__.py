import configparser
import itertools
import urllib.request

import click
import systemd.journal

from .client import CloudWatchClient
from .version import version


def get_instance_id():
    URL = 'http://169.254.169.254/latest/meta-data/instance-id'
    with urllib.request.urlopen(URL) as src:
        return src.read().decode()


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version {}'.format(version))
    ctx.exit()


python_aws_mapping = {'destination_arn': 'destinationArn',
                      'filter_name': 'filterName',
                      'filter_pattern': 'filterPattern',
                      'role_arn': 'roleArn'}


@click.command()
@click.option('--cursor', help='Store/read the journald cursor in this file')
@click.option('--logs', default='/var/log/journal',
              help='Directory to journald logs (default: /var/log/journal)')
@click.option('--prefix', default='',
              help='Log group prefix (default is blank).'
              ' Log group will be {prefix}_{instance_id}')
@click.option('--log-group', help='Name of the log group to use')
@click.option('--retention',
              type=click.Choice(
                  [str(i) for i in (0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150,
                                    180, 365, 400, 545, 731, 1827, 3653)]),
              default='0',
              help='Set retention duration of log_group in days.'
              ' Only when log group is created. 0 means infinite')
@click.option('--config', help='Path to config file', type=click.Path())
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
def main(cursor, logs, prefix, log_group, retention, config):
    if config:
        config_ = configparser.ConfigParser()
        config_.read(config)
        section = config_['jd2cw']
        cursor = section['cursor']
        logs = section.get('logs', '/var/log/journal')
        try:
            log_group = section['log-group']
        except KeyError:
            log_group = get_instance_id()
            try:
                prefix = section['prefix']
            except KeyError:
                pass
            else:
                log_group = '{}_{}'.format(prefix, log_group)
        log_group = log_group
        retention = int(section.get('retention', 0))
        subscription_filter_config = {}
        try:
            subscription_filter_section = config_['subscription-filter']
        except KeyError:
            pass
        else:
            subscription_filter_config['logGroupName'] = log_group
            for k, v in subscription_filter_section.items():
                subscription_filter_config[python_aws_mapping[k]] = v
    else:
        cursor = cursor
        logs = logs
        if not log_group:
            log_group = get_instance_id()
        if prefix:
            log_group = '{}_{}'.format(prefix, log_group)
        log_group = log_group
        retention = int(retention)
        subscription_filter_config = {}

    client = CloudWatchClient(log_group, cursor, retention,
                              subscription_filter_config)
    client.configure()

    cursor = client.load_cursor()
    with systemd.journal.Reader(path=logs) as reader:
        if cursor:
            reader.seek_cursor(cursor)
        else:
            # no cursor, start from start of this boot
            reader.this_boot()
            reader.seek_head()

        try:
            while True:
                reader.wait()
                for log_stream, messages in itertools.groupby(
                        filter(CloudWatchClient.retain_message, reader),
                        key=client.log_stream_for):
                    client.log_messages(log_stream, list(messages))
        except KeyboardInterrupt:
            pass
