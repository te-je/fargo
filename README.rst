fargo
=====

|license|

.. image:: ./doc/anim.gif

Installation
------------

You can install fargo directly from GitHub::

    > pip install git+https://github.com/te-je/fargo

That should install all the dependencies for you. If you want to install
directly from source, clone the git repository and run the standard
`python setup.py install` command.

Dependencies
~~~~~~~~~~~~

* Python 3.5+

Usage
-----

::

  Usage: fargo [OPTIONS] SEARCH [REPLACEMENT] [REPO]

  Options:
    -V, --version      show the version number and exit.
    -i, --interactive  run in interactive mode
    --help             Show this message and exit.

If ``REPLACEMENT`` is omitted, then an empty string is substituted for
matches (this does *not* perform a simple find -- you can use ``git grep``
for that and more).

``REPO`` defaults to the current directory. Currently, only Git repos are
supported.


.. |build-status| image:: https://travis-ci.org/te-je/fargo.svg?branch=develop
    :target: https://travis-ci.org/te-je/fargo/branches
    :alt: build status
    :scale: 100%

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://raw.githubusercontent.com/te-je/fargo/develop/LICENSE.txt
    :alt: License
    :scale: 100%
