import sys
from os import path

import click


__all__ = ['__version__', 'main', 'find_and_replace']


# Read the package version from the VERSION.txt file.
this_dir = path.dirname(__file__)
version_file = open(path.join(this_dir, 'VERSION.txt'), encoding='ascii')
__version__ = version_file.read().strip()
version_file.close()


def show_version_and_exit():
    click.echo(__version__)
    sys.exit(0)


def _check_and_show_version(_, __, is_set):
    if is_set:
        show_version_and_exit()


@click.command()
@click.option('--version', '-V', is_flag=True,
              callback=_check_and_show_version)
@click.argument('search', nargs=1)
@click.argument('replacement', nargs=1)
@click.argument('repo', nargs=1, required=False, default='.',
                type=click.Path(file_okay=False))
def main(**kwargs):
    find_and_replace(**kwargs)


def find_and_replace(search, replacement, *, repo='.', chardet_threshold=0.8,
                     fallback_encoding=None, force_encoding=None):
    """Find and replace items inside tracked files
    """
    raise NotImplementedError


def _iter_repo_files(repo):
    repo = path.abspath(repo)
    repo = dulwich.Repo(repo)
    for filename in repo.open_index():
        filename = filename.decode(sys.getfilesystemencoding())
        yield path.join(repo, filename)
