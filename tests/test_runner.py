from click.testing import CliRunner


def test_main_with_arguments(cursor, journal_dir):
    from jd2cw import main

    runner = CliRunner()
    result = runner.invoke(main, ['--logs={}'.format(journal_dir),
                                  '--log-group=foo',
                                  '--cursor={}'.format(cursor)])
    assert result.exit_code == 0, result.output
    assert result.output == ''


def test_main_with_config_file(config_file):
    from jd2cw import main

    runner = CliRunner()
    result = runner.invoke(main, ['--config={}'.format(config_file)])
    assert result.exit_code == 0, result.output
    assert result.output == ''
