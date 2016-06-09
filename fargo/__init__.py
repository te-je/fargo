import re
import sys
from os import path

import chardet
import click
from dulwich.repo import Repo


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
              help="show the version number and exit.",
              callback=_check_and_show_version)
@click.option('--interactive', '-i', is_flag=True,
              help='run in interactive mode')
@click.argument('search', nargs=1)
@click.argument('replacement', required=False)
@click.argument('repo', nargs=1, required=False, default='.',
                type=click.Path(file_okay=False))
def main(**kwargs):
    #kwargs['verbosity'] = verbose
    kwargs.pop('version')
    find_and_replace(**kwargs)


def find_and_replace(search, replacement, *, repo='.', chardet_threshold=0.95,
                     fallback_encoding=None, interactive=False, use_regex=False):
    """Find and replace items inside tracked files

    :param search: The text to search for. If ``use_regex`` is truthy, then
        this can be a regular expression.
    :param replacement: The substition text for matches. If ``use_regex`` is
        truthy, this can be an expansion pattern (e.g. \1 to match the first
        capture group) similar to what is passed to ``re.sub``.
    :param repo: A git repository containing cached files to perform
        substitutions in
    :param chardet_threshold: When guessing a file encoding, guesses with
        confidence below this threshold will not be used
    :param fallback_encoding: The default file encoding to use when
        the encoding can't be confidently guessed. If ``None`` is given,
        then the file is skipped.
    :param interactive: If truthy, prompt on stdin before making substitutions
    :param use_regex: If truthy, ``search`` and ``replacement`` parameters
        have have different meanings.
    """

    replacement = replacement or ""

    for filename in _iter_repo_files(repo):
        contents = _get_file_contents(
            filename,
            chardet_threshold,
            fallback_encoding
        )

        if contents is None:
            continue

        encoding, text = contents
        lines = text.splitlines(True)
        changed_lines = []

        line_iter = _iter_occurences_by_line(search, text, use_regex)
        for lineno, matches in line_iter:
            # Where does this line start in the text?
            cursor = len("".join(lines[:lineno - 1]))

            # Do the preliminary output for this line
            click.echo('{}:L{}:'.format(filename, lineno), nl=False)

            # Process this line
            chunks = _get_line_chunks(
                matches, cursor, replacement, text, use_regex
            )
            for i, (unchanged, old, new) in enumerate(chunks):
                click.echo(unchanged, nl=False)

                if old or new:
                    if interactive:
                        click.secho(str(i), bg='white', fg='black', nl=False)
                    click.secho(old, bg='red', nl=False)
                    click.secho(new, bg='green', nl=False)

            # Special case for file that doesn't end in newline
            if unchanged[-1] not in ('\n', '\r'):
                click.echo('')

            if interactive:
                # Ask which chunks to replace
                keep = _prompt_replace_items(len(chunks) - 1)
                chunks = [
                    item if i in keep
                    else [item[0], item[1], item[1]]
                    for i, item in enumerate(chunks)
                ]

            # Rebuild the line from the chunks
            changed_line = ''.join(
                ''.join((unchanged, new)) for unchanged, _, new in chunks
            )
            changed_lines.append((lineno, changed_line))

        for lineno, line in changed_lines: lines[lineno - 1] = line
        updated_text = ''.join(lines)

        if text != updated_text:
            with open(filename, 'wb') as fh:
                fh.write(updated_text.encode(encoding))


def _get_file_contents(filename, chardet_threshold, fallback_encoding):
    with open(filename, 'rb') as fh:
            data = fh.read()

    guess = chardet.detect(data)
    if guess['confidence'] > chardet_threshold:
        encoding = guess['encoding']

    else:
        encoding = fallback_encoding

    if encoding is None:
        return None

    try:
        text = data.decode(encoding)
    except UnicodeDecodeError:
        return None
    else:
        return encoding, text


def _get_line_chunks(matches, cursor, replacement, text, use_regex):
    deltas = []

    for match in matches:
        # the unchanged part, before the match
        unchanged = text[cursor: match.start()]
        sub = match.expand(replacement) if use_regex else replacement
        deltas.append([unchanged, match.group(), sub])

        # advance the cursor
        cursor = match.end()

    # Finally, add the item after the last match
    end = text.find("\n", cursor)
    unchanged = text[cursor:] if end == -1 else text[cursor: end + 1]
    deltas.append([unchanged, '', ''])

    return deltas


def _prompt_replace_items(count):
    ans = click.prompt("Accept replacements?", default='yes')

    if 'yes'.startswith(ans.lower()):
        return range(count)

    elif 'no'.startswith(ans.lower()):
        return range(0)

    else:
        try:
            repl_only = []
            for num in ans.split():
                ind = int(num.strip())
                if ind not in range(count): raise IndexError
                repl_only.append(ind)
        except:
            return _prompt_replace_items(count)
        else:
            return repl_only


def _iter_occurences_by_line(search, text, use_regex=False):
    # Caches all matches on the same line, yielding them all at once
    cache = []
    curline = 0

    for match in _iter_occurences(search, text, use_regex=use_regex):
        lineno = text.count("\n", 0, match.start()) + 1

        if curline != lineno and cache:
            yield curline, cache
            cache = []

        curline = lineno
        cache.append(match)

    if cache:
        yield curline, cache


def _iter_repo_files(repo):
    repoobj = Repo(repo)
    for filename in repoobj.open_index():
        filename = filename.decode(sys.getfilesystemencoding())
        yield path.normpath(path.join(repo, filename))


def _iter_occurences(search, text, use_regex=False):
    pattern = re.compile(search if use_regex else re.escape(search))
    last_index = 0

    match = pattern.search(text)

    while match is not None:
        yield match
        match = pattern.search(text, match.end())
