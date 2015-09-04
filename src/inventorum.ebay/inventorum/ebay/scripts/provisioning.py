# encoding: utf-8
from __future__ import absolute_import
import os
import logging
from pipes import quote
import subprocess

from inventorum.util.paste import boostrap_from_config

import plac

log = logging.getLogger(__name__)


def execute_shell_command(cmd):
    log.debug(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        log.error(stderr)
        exit(proc.returncode)
    return stdout


def _provision_db(db_name, with_drop):
    from django.conf import settings

    db = settings.DATABASES["default"]
    db_host = db["HOST"]
    db_user = db["USER"]
    db_pass = db['PASSWORD']

    sandbox_root = settings.BUILDOUT_ROOT
    log.debug("sandbox root is %s", sandbox_root)
    sandbox_exec_path = os.path.normpath(os.path.join(sandbox_root, "parts", "postgresql", "bin"))

    if os.path.isdir(sandbox_exec_path):
        log.info("Running in sandbox mode")

        def psql(psql_cmd):
            return """echo "{psql_cmd}" | {sandbox_exec_path}/psql -h {db_host} -d postgres"""\
                .format(psql_cmd=psql_cmd, sandbox_exec_path=sandbox_exec_path, db_host=os.path.normpath(db_host))

        create_user = psql("CREATE USER {db_user} WITH PASSWORD '{db_pass}' CREATEDB;".format(db_user=db_user,
                                                                                              db_pass=db_pass))

        create_db = psql("CREATE DATABASE {db_name} OWNER {db_user} "
                         "ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8';".format(db_name=db_name,
                                                                                                   db_user=db_user))
    else:
        log.info("Running in system mode")

        def psql(psql_cmd):
            return "su - postgres -c {shell_cmd}"\
                .format(shell_cmd=quote("""echo "{psql_cmd}" | psql -d postgres""".format(psql_cmd=psql_cmd)))

        create_user = psql("CREATE ROLE {db_user} ENCRYPTED PASSWORD '{db_pass}' "
                           "NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN;".format(db_user=db_user,
                                                                                       db_pass=db_pass))

        create_db = psql("CREATE DATABASE {db_name};"
                         "GRANT ALL PRIVILEGES ON DATABASE {db_name} to {db_user};".format(db_name=db_name,
                                                                                           db_user=db_user))

    drop_db = psql("DROP DATABASE {db_name}".format(db_name=db_name))

    # check if database user already exists
    stdout = execute_shell_command(" ".join([psql("\du"), "|", "grep {db_user}".format(db_user=db_user), "|", "wc -l"]))
    if stdout.strip() == "0":
        log.info("Creating database user '%s'...", db_user)
        execute_shell_command(create_user)
    else:
        log.info("Database user '%s' already exists", db_user)

    # check if database already exists
    stdout = execute_shell_command(" ".join([psql("\list"), "|", "grep {db_name}".format(db_name=db_name), "|", "wc -l"]))
    if stdout.strip() != "0":
        if not with_drop:
            log.info("Database '%s' already exists", db_name)
            exit(0)
        else:
            log.info("Dropping database '%s'...", db_name)
            execute_shell_command(drop_db)

    log.info("Creating database '%s'...", db_name)
    execute_shell_command(create_db)


def provision_db():
    @plac.annotations(
        config_file=plac.Annotation("paster config file", "positional", None, str),
        db_name=plac.Annotation("name of the database to provision", "positional", None, str),
        with_drop=plac.Annotation("drop database option", "flag", "D")
    )
    def init_and_execute(config_file, db_name, with_drop=False):
        boostrap_from_config(config_file)
        _provision_db(db_name, with_drop)

    plac.call(init_and_execute, eager=False)


def _provision_rabbitmq():
    from django.conf import settings

    rabbit_vhost = settings.RABBITMQ_VHOST
    rabbit_user = settings.RABBITMQ_USER
    rabbit_pass = settings.RABBITMQ_PASSWORD

    sandbox_root = settings.BUILDOUT_ROOT
    log.debug("sandbox root is %s", sandbox_root)
    sandbox_exec_path = os.path.join(sandbox_root, "parts", "rabbitmq", "sbin")

    if os.path.isdir(sandbox_exec_path):
        log.info("Running in sandbox mode")

        def rabbitmqctl(cmd):
            return "{sandbox_exec_path}/rabbitmqctl {cmd}".format(sandbox_exec_path=sandbox_exec_path, cmd=cmd)
    else:
        log.info("Running in system mode")

        def rabbitmqctl(cmd):
            return "sudo rabbitmqctl {cmd}".format(cmd=cmd)

    # check if vhost already exists
    stdout = execute_shell_command(" ".join([rabbitmqctl("list_vhosts"), "|", "grep '^{vhost}$'".format(vhost=rabbit_vhost), "|", "wc -l"]))
    if stdout.strip() == "0":
        log.info("Creating vhost '%s'...", rabbit_vhost)
        execute_shell_command(rabbitmqctl("add_vhost {vhost}".format(vhost=rabbit_vhost)))
    else:
        log.info("vhost '%s' already exists", rabbit_vhost)

    # check if user already exists
    stdout = execute_shell_command(" ".join([rabbitmqctl("list_users"), "|", "grep '^{user}'".format(user=rabbit_user), "|", "wc -l"]))
    if stdout.strip() == "0":
        log.info("Creating user '%s'...", rabbit_user)
        execute_shell_command(rabbitmqctl("add_user {username} {password}".format(username=rabbit_user, password=rabbit_pass)))
        log.info("Granting permissions for user '%s' to vhost '%s'...", rabbit_user, rabbit_vhost)
        execute_shell_command(rabbitmqctl("set_permissions -p {vhost} {username} '.*' '.*' '.*'".format(vhost=rabbit_vhost, username=rabbit_user)))
    else:
        log.info("User '%s' already exists", rabbit_user)

    log.info("Done. Go crazy!")


def provision_rabbitmq():
    def init_and_execute(config_file):
        boostrap_from_config(config_file)
        _provision_rabbitmq()

    plac.call(init_and_execute, eager=False)
