import pytest
from fargo import __version__, show_version_and_exit


def test_show_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        show_version_and_exit()

    assert exc_info.value.code == 0

    out, err = capsys.readouterr()
    assert out == __version__ + "\n"
