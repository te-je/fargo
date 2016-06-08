"""Checks that the command line interface calls the right functions"""

import pytest
from fargo import main


@pytest.mark.parametrize('args', [
    ['-V'],
    ['--version']
])
def test_version(mocker, args):
    show_version = mocker.patch('fargo.show_version_and_exit')

    with pytest.raises(SystemExit):
        main(args)

    assert show_version.called_once_with()


@pytest.mark.parametrize('args, expected_args, expected_kwargs', [
    (['foo', 'bar'], ('foo', 'bar'), {'repo': '.'}),
    (['foo', 'bar', 'repo'], ('foo', 'bar'), {'repo': 'repo'})
])
def test_find_and_replace(mocker, args, expected_args, expected_kwargs):
    far = mocker.patch('fargo.find_and_replace')

    with pytest.raises(SystemExit):
        main(args)

    assert far.called_once_with(*expected_args, **expected_kwargs)
