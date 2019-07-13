
# Django Polls Improved

This repository is a collection of some improvements to the 
[Django polls tutorial](https://docs.djangoproject.com/en/2.2/intro/tutorial01/).
The improvements mainly concern the setup.

## Overview of Improvements

- [Pre-commit hooks](#pre-commit-hooks)

# <a name="requirements-and-installation"/>Requirements & Installation

This project was written using Python 3.7, Django 2.2 and Ubuntu 18.04.

First, set up a virtual environment.
1. Change the directory to this project's root and type `python -m venv venv` to create a virtual environment named `venv`
2. Activate the virtual environment (`(venv)` should appear before the directory)
    1. On Windows: `venv\Scripts\activate`
    2. On Linux: `source venv/bin/activate`
3. Install the requirements with `pip install -r requirements.txt`

# <a name="pre-commit-hooks"/>Pre-commit hooks

Pre-commit hooks are a way to execute hooks before every commit. For example, to format
your code before every commit. To do this we use the [pre-commit framework](https://pre-commit.com/), which can 
be installed via `pip install pre-commit`.

The hooks are specified in a file called `.pre-commit-config.yaml`. 
This project uses three hooks: 
- [black](https://github.com/python/black) to format your Python code
- [flake8](http://flake8.pycqa.org/en/latest/) for style enforcements
- [isort](https://github.com/timothycrosley/isort) to sort the imports

Black is further configured in `pyproject.toml`, isort and flake8 are further configured
in `setup.cfg`. This is mostly for everything to be compatible with each other, otherwise black
will format something, then isort will format it differently, then black wants to format it again, etc.
Also, I prefer the Django settings formatted as they are, so they are explicitly excluded in `.pre-commit-config.yaml`.

To install the pre-commit hooks type `pre-commit install`.
Pre-commit hooks only use the files staged for commit, to run it on every file type `pre-commit run --all-files`.
Note that if a file is reformatted during a commit, the commit will fail. The consequence is that
you will have to *commit twice* in general. The first commit will fail and format the files, the second commit
validates that the files are formatted and goes through.
