# Contributing

Contributing to Mist is easy: just open a [pull
request](https://help.github.com/articles/using-pull-requests/). Make
`main` the destination branch on the Mist repository and add a full
description of the intended changes.

Your pull request must be reviewed by at least one Mist developer.

## Automatic commit checks

You can use `pre-commit` to ensure local changes are ready to be submitted in a
pull request. It can be installed locally using: `pip install pre-commit`, then it
must be setup for the repository: `pre-commit install`. Formatting and other checks
are then run for every commit.

Adding `--no-verify` to the commit options can be used to skip these checks for a given commit, if needed.

Checks can always also be done manually.
