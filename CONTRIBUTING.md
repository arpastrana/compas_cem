# Contributing

Contributions are welcome and very much appreciated!

## Code contributions

We accept code contributions through pull requests.
In short, this is how that works.

1. Fork [the repository](https://github.com/arpastrana/compas_cem) and clone the fork.
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you do not have it.
3. Create the development environment. This installs a supported Python, the package in editable mode, the plotter, the viewer and every development tool, pinned by `uv.lock`:

   ```bash
   uv sync --extra dev
   ```

   Prefix commands with `uv run` to execute them inside that environment, no activation needed.
   The lock covers Python 3.11 to 3.13. To work on Python 3.9 or 3.10, as Rhino 8 runs 3.9, or if you prefer `pip`, create a virtual environment and run `pip install -e ".[dev]"`.

4. Install the pre-commit hooks (they run `ruff` and basic file checks on each commit, and check its message):

   ```bash
   uv run pre-commit install
   ```

5. Make sure all tests pass:

   ```bash
   uv run invoke test
   ```

6. Start making your changes to the **main** branch (or branch off of it).
7. Make sure all tests still pass:

   ```bash
   uv run invoke test
   ```

8. Add yourself to the *Contributors* section of `AUTHORS.md`.
9. Commit your changes and push your branch to GitHub.
10. Create a [pull request](https://help.github.com/articles/about-pull-requests/) through the GitHub website.

During development, use [pyinvoke](http://docs.pyinvoke.org/) tasks on the
command line to ease recurring operations (prefix each with `uv run`):

* `invoke clean`: Clean all generated artifacts.
* `invoke check`: Run various code and documentation style checks.
* `invoke docs`: Generate documentation.
* `invoke test`: Run all tests and checks in one swift command.
* `invoke`: Show available tasks.

## Bug reports

When [reporting a bug](https://github.com/arpastrana/compas_cem/issues) please include:

* Operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

## Feature requests

When [proposing a new feature](https://github.com/arpastrana/compas_cem/issues) please include:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
