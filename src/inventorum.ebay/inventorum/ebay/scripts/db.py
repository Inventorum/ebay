# encoding: utf-8
from __future__ import absolute_import
import os
import logging
from pipes import quote
import subprocess

from inventorum.util.paste import boostrap_from_config

import plac

log = logging.getLogger(__name__)


def _db_provision(db_name, with_drop):
    from django.conf import settings

    def execute(cmd):
        log.debug(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            log.error(stderr)
            exit(proc.returncode)
        return stdout

    db = settings.DATABASES["default"]
    db_host = db["HOST"]
    db_user = db["USER"]
    db_pass = db['PASSWORD']

    sandbox_root = settings.BUILDOUT_ROOT
    log.debug("sandbox root is %s", sandbox_root)
    sandbox_exec_path = os.path.join(sandbox_root, "parts", "postgresql", "bin")

    if os.path.isdir(sandbox_exec_path):
        log.info("Running in sandbox mode")

        def psql(psql_cmd):
            return """echo "{cmd}" | {sandbox_exec_path}/psql -h {host} -d postgres"""\
                .format(cmd=psql_cmd, sandbox_exec_path=sandbox_exec_path, host=db_host)

        create_user = psql("CREATE USER {username} WITH PASSWORD '{password}' CREATEDB;".format(username=db_user,
                                                                                                password=db_pass))

        create_db = psql("CREATE DATABASE {db_name} OWNER {owner} "
                         "ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8';".format(db_name=db_name,
                                                                                                   owner=db_user))
    else:
        log.info("Running in system mode")

        def psql(psql_cmd):
            return "su - postgres -c {shell_cmd}"\
                .format(shell_cmd=quote("""echo "{psql_cmd}" | psql -d postgres""".format(psql_cmd=psql_cmd)))

        create_user = psql("CREATE ROLE {username} ENCRYPTED PASSWORD '{password}' "
                           "NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN;".format(username=db_user,
                                                                                       password=db_pass))

        create_db = psql("CREATE DATABASE {db_name};"
                         "GRANT ALL PRIVILEGES ON DATABASE {db_name} to {username};".format(db_name=db_name,
                                                                                            db_user=db_user))

    drop_db = psql("DROP DATABASE {db_name}".format(db_name=db_name))

    # check if database user already exists
    stdout = execute(" ".join([psql("\du"), "|", "grep {username}".format(username=db_user), "|", "wc -l"]))
    if stdout.strip() == "0":
        log.info("Creating database user '%s'...", db_user)
        execute(create_user)
    else:
        log.info("Database user '%s' already exists", db_user)

    # check if database already exists
    stdout = execute(" ".join([psql("\list"), "|", "grep {db_name}".format(db_name=db_name), "|", "wc -l"]))
    if stdout.strip() != "0":
        if not with_drop:
            log.info("Database '%s' already exists", db_name)
            exit(0)
        else:
            log.info("Dropping database '%s'...", db_name)
            execute(drop_db)

    log.info("Creating database '%s'...", db_name)
    execute(create_db)


def db_provision():
    @plac.annotations(
        config_file=plac.Annotation("paster config file", "positional", None, str),
        db_name=plac.Annotation("name of the database to provision", "positional", None, str),
        with_drop=plac.Annotation("drop database option", "flag", "D")
    )
    def init_and_execute(config_file, db_name, with_drop=False):
        boostrap_from_config(config_file)
        _db_provision(db_name, with_drop)

    plac.call(init_and_execute, eager=False)
