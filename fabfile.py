from getpass import getpass

from fabric import Config, Connection, task
from invoke import Responder
from invoke import run as run_local


REPOSITORY_URL = "github.com/janbrrr/django-polls-improved.git"  # without the https://
HOSTS = {
    "local": {"address": "localhost"},
    "prod": {"address": "YOUR-HOST", "project_dir": "~/python/django-polls-improved"},
}

DOCKER_RUN_CMD = "docker-compose up -d --build"
DOCKER_STOP_CMD = "docker-compose down"
DOCKER_STATUS_CMD = "docker-compose ps"
DOCKER_LOGS_CMD = "docker-compose logs"


@task
def setup(context):
    host = context.host
    if host not in HOSTS or host == "local":
        raise RuntimeError("Run 'fab -H <host> setup' where <host> is 'prod'")
    remote_user = input("User: ")
    remote_password = getpass("Password: ")
    config = Config(overrides={"sudo": {"password": remote_password}})
    remote_address = HOSTS[host]["address"]
    remote_project_dir = HOSTS[host]["project_dir"]
    with Connection(
        host=remote_address, user=remote_user, connect_kwargs={"password": remote_password}, config=config
    ) as connection:
        git_clone(connection, remote_project_dir)
        install_python(connection, remote_password)
        install_docker(connection)
        # Install docker-compose in a virtual environment
        create_venv(connection, remote_project_dir)
        run_in_venv(connection, remote_project_dir, "pip install wheel")  # Required for building
        run_in_venv(connection, remote_project_dir, "pip install docker-compose")
        print()
        print("Setup complete!")
        print("Remember to put your certificate in 'nginx/my_cert.pem' and your key in 'nginx/my_key.pem'")
        print("or run 'fab -H prod create-certificate' to create a self-signed certificate")
        print("Remember to create the '.env' and 'env.db' files to configure the Django and Postgres.")


@task
def create_certificate(context):
    host = context.host
    if host not in HOSTS:
        raise RuntimeError("Run 'fab -H <host> create-certificate' where <host> is 'local' or 'prod'")
    command = "openssl req -x509 -newkey rsa:4096 -keyout nginx/my_key.pem -out nginx/my_cert.pem -days 365 --nodes"
    if host == "local":
        run_local(command)
    else:
        remote_user = input("User: ")
        remote_password = getpass("Password: ")
        remote_address = HOSTS[host]["address"]
        remote_project_dir = HOSTS[host]["project_dir"]
        with Connection(
            host=remote_address, user=remote_user, connect_kwargs={"password": remote_password}
        ) as connection:
            with connection.cd(remote_project_dir):
                connection.run(command)


@task
def create_superuser(context):
    host = context.host
    if host not in HOSTS:
        raise RuntimeError("Run 'fab -H <host> create-superuser' where <host> is 'local' or 'prod'")
    command = "docker-compose exec web python manage.py createsuperuser"
    if host == "local":
        run_local(command)
    else:
        remote_user = input("User: ")
        remote_password = getpass("Password: ")
        remote_address = HOSTS[host]["address"]
        remote_project_dir = HOSTS[host]["project_dir"]
        with Connection(
            host=remote_address, user=remote_user, connect_kwargs={"password": remote_password}
        ) as connection:
            run_in_venv(connection, remote_project_dir, command, pty=True)


@task
def deploy(context):
    host = context.host
    if host not in HOSTS:
        raise RuntimeError("Run 'fab -H <host> deploy' where <host> is 'local' or 'prod'")
    if host == "local":
        run_local(DOCKER_RUN_CMD)
    else:
        remote_user = input("User: ")
        remote_password = getpass("Password: ")
        remote_address = HOSTS[host]["address"]
        remote_project_dir = HOSTS[host]["project_dir"]
        with Connection(
            host=remote_address, user=remote_user, connect_kwargs={"password": remote_password}
        ) as connection:
            git_pull(connection, remote_project_dir)
            run_in_venv(connection, remote_project_dir, DOCKER_RUN_CMD)


@task
def stop(context):
    host = context.host
    if host not in HOSTS:
        raise RuntimeError("Run 'fab -H <host> stop' where <host> is 'local' or 'prod'")
    if host == "local":
        run_local(DOCKER_STOP_CMD)
    else:
        remote_user = input("User: ")
        remote_password = getpass("Password: ")
        remote_address = HOSTS[host]["address"]
        remote_project_dir = HOSTS[host]["project_dir"]
        with Connection(
            host=remote_address, user=remote_user, connect_kwargs={"password": remote_password}
        ) as connection:
            run_in_venv(connection, remote_project_dir, DOCKER_STOP_CMD)


@task
def status(context):
    host = context.host
    if host not in HOSTS:
        raise RuntimeError("Run 'fab -H <host> status' where <host> is 'local' or 'prod'")
    if host == "local":
        run_local(DOCKER_STATUS_CMD)
    else:
        remote_user = input("User: ")
        remote_password = getpass("Password: ")
        remote_address = HOSTS[host]["address"]
        remote_project_dir = HOSTS[host]["project_dir"]
        with Connection(
            host=remote_address, user=remote_user, connect_kwargs={"password": remote_password}
        ) as connection:
            run_in_venv(connection, remote_project_dir, DOCKER_STATUS_CMD)


@task
def logs(context):
    host = context.host
    if host not in HOSTS:
        raise RuntimeError("Run 'fab -H <host> logs' where <host> is 'local' or 'prod'")
    if host == "local":
        run_local(DOCKER_LOGS_CMD)
    else:
        remote_user = input("User: ")
        remote_password = getpass("Password: ")
        remote_address = HOSTS[host]["address"]
        remote_project_dir = HOSTS[host]["project_dir"]
        with Connection(
            host=remote_address, user=remote_user, connect_kwargs={"password": remote_password}
        ) as connection:
            run_in_venv(connection, remote_project_dir, DOCKER_LOGS_CMD)


def install_docker(connection):
    connection.run("curl -fsSL https://get.docker.com -o get-docker.sh")
    connection.sudo("sh get-docker.sh")
    connection.sudo("usermod -a -G docker $USER")


def install_python(connection, sudo_password):
    connection.sudo("apt-get update -qy")
    connection.sudo(
        "apt-get install -qy build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev "
        "libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev"
    )
    connection.run("wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz")
    connection.run("tar xf Python-3.7.3.tar.xz")
    with connection.cd("Python-3.7.3"):
        connection.run("./configure")
        connection.run("make")
        # Running connection.sudo(...) will fail for the next command, so we need a workaround
        # Make sure to adjust the pattern if you are using a different language
        sudo_responder = Responder(pattern=r"\[sudo\] password", response=f"{sudo_password}\n")
        connection.run("sudo make altinstall", pty=True, watchers=[sudo_responder])
    connection.sudo("rm -r Python-3.7.3")
    connection.sudo("rm Python-3.7.3.tar.xz")


def git_clone(connection, project_dir):
    git_username = input("Git username: ")
    git_password = getpass("Git password: ")
    connection.run(f"git clone https://{git_username}:{git_password}@{REPOSITORY_URL} {project_dir}")


def git_pull(connection, project_dir):
    with connection.cd(project_dir):
        git_username = input("Git username: ")
        git_password = getpass("Git password: ")
        connection.run(f"git pull https://{git_username}:{git_password}@{REPOSITORY_URL} master")


def create_venv(connection, project_dir):
    with connection.cd(project_dir):
        connection.run("python3.7 -m venv venv")


def run_in_venv(connection, project_dir, command, **kwargs):
    with connection.cd(project_dir):
        connection.run(f"source venv/bin/activate && {command}", **kwargs)
