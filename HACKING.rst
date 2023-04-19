TradeZero Frontend Guidelines
=============================

This application follows a set of style guidelines for clarity.
Evem though this is a small test project, it is desired to follow
common accepted standards to help understand and maintain the code..

General
-------

- Follow `pep8` standard

.. _`pep8`: http://www.python.org/dev/peps/pep-0008/

- Use only UNIX style newlines (``\n``), not Windows style (``\r\n``)
- It is preferred to wrap long lines in parentheses and not a backslash
  for line continuation.
- Do not write ``except:``, use ``except Exception:`` at the very least.
  When catching an exception you should be as specific so you don't mistakenly
  catch unexpected exceptions.
- Include your name with TODOs as in ``# TODO(yourname)``. This makes
  it easier to find out who the author of the comment was.
- Don't use author tags. We use version control instead.
- Don't put vim configuration in source files (off by default).
- Delay string interpolations at logging calls (off by default).
- Do not shadow a built-in or reserved words, as it makes the code
  harder to understand.

Creating Unit Tests
-------------------
For every new feature, unit tests should be created that both test and
(implicitly) document the usage of said feature. If submitting a patch for a
bug that had no unit test, a new passing unit test should be added. If a
submitted bug fix does have a unit test, be sure to add a new one that fails
without the patch and passes with the patch.

Commit Messages
---------------
Using a common format for commit messages will help keep our git history
readable.

The first line of the commit message should provide an accurate description
of the change and must be under 50 chars. It must be followed by a blank line.

Following your brief summary, provide a more detailed description of
the patch, manually wrapping the text at 72 characters. This
description should provide enough detail that one does not have to
refer to external resources to determine its high-level functionality.

