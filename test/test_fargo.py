import sys
import pytest
from dulwich.repo import Repo
from fargo import find_and_replace


suits = [u'\u2660', u'\u2665', u'\u2666', u'\u2663']
ranks = list(str(i) for i in range(2, 11)) + ['J', 'Q', 'K', 'A']
deck_text = u"This here is a deck of cards man:\n\n{}".format(
    "\n".join(''.join((r, s)) for s in suits for r in ranks)
)


@pytest.fixture
def repo(tmpdir):
    test_file = tmpdir.join('test_file')
    test_file.write(u"For here we have\nA test file\nwith only useless stuff\n")

    # Add some unicode data
    for encoding in ('utf8', 'utf16'):
        deck_file = tmpdir.join('deck').join(encoding)
        deck_file.write_text(deck_text, encoding=encoding, ensure=True)

    repo = Repo.init(tmpdir.strpath)
    repo.stage([b'test_file', b'deck/utf8', b'deck/utf16'])
    repo.do_commit(b'initial',
                   committer=b'Te-je Rodgers <tjd.roders@gmail.com>')

    return repo


@pytest.mark.parametrize('interactive', [True, False])
@pytest.mark.parametrize('encoding', ['utf8', 'utf16'])
@pytest.mark.parametrize('search,sub', [
    (u'\u2660', u'S'),
    (u'\u2665', u'\u2661'),
    (u'\u2666', u'of Diamonds')
])
def test_replace_unicode_cards(mocker, repo, tmpdir, interactive, encoding,
                               search, sub):
    mocker.patch('fargo.click.prompt').return_value = 'yes'
    find_and_replace(search, sub, repo=str(tmpdir), interactive=interactive)

    deck_file = tmpdir.join('deck').join(encoding)
    new_deck_text = deck_file.read_text(encoding=encoding)

    assert deck_text.replace(search, sub) == new_deck_text


@pytest.mark.parametrize('encoding', ['utf8', 'utf16'])
@pytest.mark.parametrize('search,sub', [
    (u'\u2660', 'S'),
    (u'\u2665', '\u2661'),
    (u'\u2666', 'of Diamonds')
])
def test_replace_unicode_cards_reject_interactive(
        mocker, repo, tmpdir, encoding, search, sub):
    mocker.patch('fargo.click.prompt').return_value = 'no'
    find_and_replace(search, sub, repo=str(tmpdir), interactive=True)

    deck_file = tmpdir.join('deck').join(encoding)
    new_deck_text = deck_file.read_text(encoding=encoding)

    assert deck_text.replace(search, sub) != new_deck_text


def test_interactive_specific_items(mocker, repo, tmpdir):
    # Replace only the first and second items
    mocker.patch('fargo.click.prompt').return_value = '0 1'
    find_and_replace('e', 'E', repo=str(tmpdir), interactive=True)

    test_file = tmpdir.join('test_file')
    new_text = test_file.read()
    expected_text = u"For hErE we have\nA tEst filE\nwith only usElEss stuff\n"

    assert new_text == expected_text


@pytest.mark.parametrize('search,sub', [
    (u'\u2660', 'S'),
    (u'\u2665', '\u2661'),
    (u'\u2666', 'of Diamonds')
])
def test_chardet_threshold(mocker, repo, tmpdir, search, sub):
    find_and_replace(search, sub, repo=str(tmpdir),
                     chardet_threshold=1, interactive=False)

    deck_file = tmpdir.join('deck').join('utf8')
    new_deck_text = deck_file.read_text(encoding='utf8')

    assert deck_text.replace(search, sub) != new_deck_text
