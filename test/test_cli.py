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

    show_version.assert_called_once_with()


@pytest.mark.parametrize('args, expected_args, expected_kwargs', [
    (['foo', 'bar'], (),
     {'repo': u'.', 'search': u'foo', 'replacement': u'bar',
      'interactive': False}),

    (['-i', 'foo', 'bar'], (),
     {'repo': u'.', 'search': u'foo', 'replacement': u'bar',
      'interactive': True}),

    (['--interactive', 'foo', 'bar'], (),
     {'repo': u'.', 'search': u'foo', 'replacement': u'bar',
      'interactive': True}),

    (['foo', 'bar', 'repo'], (),
     {'repo': 'repo', 'search': u'foo', 'replacement': u'bar',
      'interactive': False})
])
def test_find_and_replace(mocker, args, expected_args, expected_kwargs):
    far = mocker.patch('fargo.find_and_replace')

    with pytest.raises(SystemExit):
        main(args)

    far.assert_called_once_with(*expected_args, **expected_kwargs)
