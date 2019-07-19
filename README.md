
# Django Polls Improved

This repository is a collection of some improvements to the 
[Django polls tutorial](https://docs.djangoproject.com/en/2.2/intro/tutorial01/).
The improvements mainly concern the setup.

## Overview of Improvements

- [Pre-commit hooks](#pre-commit-hooks)
- [Sphinx documentation](#sphinx-docs)
- [Docker and Docker Compose](#docker)
- [Fabric for remote execution](#fabric)

# <a name="requirements-and-installation"/>Requirements & Installation

This project was written using Python 3.7, Django 2.2 and Ubuntu 18.04.

First, set up a virtual environment.
1. Change the directory to this project's root and type `python3.7 -m venv venv` to create a virtual environment named `venv`
2. Activate the virtual environment (`(venv)` should appear before the directory)
    1. On Windows: `venv\Scripts\activate`
    2. On Linux: `source venv/bin/activate`
3. Install the requirements with `pip install -r requirements.txt`

# <a name="pre-commit-hooks"/>Pre-commit hooks

[Commit 4358963947ee1c0059fce758f2c435acabcab4e0](https://github.com/janbrrr/django-polls-improved/commit/4358963947ee1c0059fce758f2c435acabcab4e0)

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

# <a name="sphinx-docs"/>Sphinx documentation

[Commit f757f954d576662f7b87476201d1931fa4208420](https://github.com/janbrrr/django-polls-improved/commit/f757f954d576662f7b87476201d1931fa4208420)

The documentation is build using [Sphinx](http://www.sphinx-doc.org) with the 
[Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io).

First, a new app called `docs` is created with `python manage.py startapp docs`
and this app is added to the `INSTALLED_APPS` in `mysite.settings`.
Next, sphinx is set up via `sphinx-quickstart` and the created file in `docs/source/conf.py` is
configured to use the correct Django settings to allow for autodoc. This requires us to exclude the file
for the pre-commit hooks as isort and flake8 will complain.

The docs will be served at the `/docs/` url as configured in `docs/urls.py` via Django's built-in 
[static.serve](https://docs.djangoproject.com/en/2.2/_modules/django/views/static/) view.

For convenience, `manage.py` is changed to run `make html` whenever `manage.py runserver` is run.

# <a name="docker"/>Docker and Docker Compose

[Commit 23bbdd4cb6887981f00df3acd4a4478003be209d](https://github.com/janbrrr/django-polls-improved/commit/23bbdd4cb6887981f00df3acd4a4478003be209d)

This section requires [Docker](https://docs.docker.com/install/) and 
[Docker Compose](https://docs.docker.com/compose/install/). 
It was developed using Docker v18.09.7 and Docker Compose v1.24.0 and is based on 
[this blog post by Michael Herman](https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/).

The basic Docker commands are:

- `docker-compose up -d --build` to build and start the services
- `docker-compose down` to shutdown the services
- `docker-compose logs` to view the logs
- `docker-compose exec web python manage.py createsuperuser` to create a superuser

Note that you have to visit `https://localhost/polls/` or some other page as the polls example
does not define a view at `https://localhost`.

We distinguish four services in the `docker-compose.yml` file:

- web: Django and [Gunicorn](https://gunicorn.org/)
- db: [Postgres](https://www.postgresql.org/)
- nginx: [NGINX](https://www.nginx.com/)
- memcached: [Memcached](https://memcached.org/)

This setup requires additional dependencies for the Django application, therefore a `requirements-prod.txt` is added.

The next step is to split the settings into development and production settings, because secrets like
the (production) secret key and the database credentials should be defined in environment
variables and not be hard-coded in the settings. 
The settings are split into `settings/base.py`, `settings/development.py` and `settings/production.py`.
By default `settings/__init__.py` will import the base settings and try to import the development settings.
If the import fails, production settings will be used. 
In other words, to use the production settings, `settings/development.py` will be deleted in the `Dockerfile`.

In order to handle database migrations more easily they will be gathered in the same directory `migrations/`.
This means that the migrations will no longer be located in `<app-name>/migrations/`, but in `migrations/<app-name>/`.
This way they can be stored in a docker volume. The changes are in `settings/base.py`.

### web service

The `Dockerfile` for the web service is in the root directory and it uses `entrypoint.sh` as entrypoint.

As specified in `docker-compose.yml` the web service uses two volumes: one for the *static files*
and one for the *migrations*. The volume with the static files will be shared with the nginx service.

The `docker-compose.yml` also specifies that the web service uses an evironment file named `.env`.
It should contain the secret key and the database credentials (and should not be committed).
Below is an example. Note that the `SQL_HOST` is `db`, because Docker Compose creates a virtual
network with all the services and the database service is named as `db`.

```
# .env
SECRET_KEY=change_me
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=hello_django_prod
SQL_USER=hello_django
SQL_PASSWORD=hello_django
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres
```

### db service

The db service does not need a Dockerfile as the postgres image contains everything we need.
The only thing is missing is an environment file containing the configuration of the database.
We create a file called `.env.db` in the root directory that looks as follows. Make sure it matches the config
for the web service.

```
# .env.db
POSTGRES_USER=hello_django
POSTGRES_PASSWORD=hello_django
POSTGRES_DB=hello_django_prod
```

Note that the `docker-compose.yml` file configures the db service to use a volume to keep the data persistent.

### nginx service

The nginx service requires additional configuration. The files are located at `nginx/`.
First, there is the NGINX configuration at `nginx/nginx.conf` and then the `nginx/Dockerfile`
that replaces the default config with our configuration. Note that it connects to `web:8000`,
as exposed via the `docker-compose.yml` file.

Moreover, the `nginx.conf` file uses SSL and the `Dockerfile` expects the certificate to be in
`nginx/my_cert.pem` and the private key to be located at `nginx/my_key.pem`. 
Note the port mappings `80:80` and `443:443` in `docker-compose.yml`.

You can create a self-signed certificate with the following command:

`openssl req -x509 -newkey rsa:4096 -keyout nginx/my_key.pem -out nginx/my_cert.pem -days 365 --nodes`

### memcached service

The official memcached image already contains everything, so no further files are necessary.
The only thing we have to do is to configure `mysite/settings/production.py` to use the correct host.
Again, according to `docker-compose.yml` this service is called `memcached` and it exposes the (default) `11211` port,
therefore the location of the cache server is `memcached:11211`.

# <a name="fabric"/>Fabric

[Commit ca745c8335463f3ab015db335575891466b321c7](https://github.com/janbrrr/django-polls-improved/commit/ca745c8335463f3ab015db335575891466b321c7)

[Fabric](http://www.fabfile.org/) is a library for remote shell execution via SSH. We can use it to automate tasks
like setting up a machine, deployment and more.

This example is tailored to using a Raspberry Pi 3 with Raspbian Stretch as production machine.
First you have to configure the production machine at the top of `fabfile.py` (the `prod` host).
Additionally, you have to add the production address to the `ALLOWED_HOSTS` in `mysite/settings/production.py`.

The tasks are defined `fabfile.py` and can be listed with the command `fab --list`.
The way the tasks are implemented you have to run them as ``fab -H <host> <cmd>`` where ``<host>``
is either ``local`` or ``prod``. For example, to run the deploy task locally type `fab -H local deploy`.
The following tasks are implemented:

- `setup`: Sets up the Raspberry Pi from scratch. Installs Python 3.7, Docker, Docker Compose and clones the repository.
- `create-certificate`: Creates a self-signed certificate and places it in the location expected by the `Dockerfile`
- `deploy`: Pulls the latest changes from the repository, builds and starts everything
- `create-superuser`: Runs `python manage.py createsuper` in the web service
- `status`: Displays the status of the services
- `logs`: Displays the logs of the services
- `stop`: Stops the services
