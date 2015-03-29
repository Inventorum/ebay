# encoding: utf-8
from __future__ import absolute_import
import os
import logging
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
        if stderr != "":
            log.error(stderr)
            exit(proc.returncode)
        return stdout

    db = settings.DATABASES["default"]
    DB_HOST = db["HOST"]
    DB_USERNAME = db["USER"]
    DB_PASSWORD = db['PASSWORD']

    sandbox_root = settings.BUILDOUT_ROOT
    log.debug("sandbox root is %s", sandbox_root)
    sandbox_exec_path = os.path.join(sandbox_root, "parts", "postgresql", "bin")

    if os.path.isdir(sandbox_exec_path):
        log.info("Running in sandbox mode")

        def psql(cmd):
            return "{sandbox_exec_path}/psql -h {host} postgres " \
                   " -c \"{cmd}\"".format(sandbox_exec_path=sandbox_exec_path,
                                                                host=DB_HOST, username=DB_USERNAME, cmd=cmd)

        createuser = psql("CREATE USER {username} WITH PASSWORD '{password}' CREATEDB;".format(username=DB_USERNAME,
                                                                                               password=DB_PASSWORD))

    else:
        log.info("Running in system mode")

        def psql(psql):
            return 'su - postgres -c "psql -d postgres -c \"{cmd}\""'.format(host=DB_HOST, cmd=psql)

        createuser = psql("CREATE ROLE {username} ENCRYPTED PASSWORD '{password}' "
                          "NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN;".format(username=DB_USERNAME,
                                                                                      password=DB_PASSWORD))

    # check if database user already exists
    stdout = execute(" ".join([psql("\du"), "|", "grep {username}".format(username=DB_USERNAME), "|", "wc -l"]))
    if stdout.strip() == "0":
        log.info("Creating database user '%s'...", DB_USERNAME)
        execute(createuser)
    else:
        log.info("Database user '%s' already exists", DB_USERNAME)

    # check if database already exists
    stdout = execute(" ".join([psql("\list"), "|", "grep {db_name}".format(db_name=db_name), "|", "wc -l"]))
    if stdout.strip() != "0":
        if not with_drop:
            log.info("Database '%s' already exists", db_name)
            exit(0)
        else:
            log.info("Dropping database '%s'...", db_name)
            execute(psql("DROP DATABASE {db_name}".format(db_name=db_name)))

    log.info("Creating database '%s'...", db_name)
    execute(psql("CREATE DATABASE {db_name} OWNER {owner} "
                 "ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8';".format(db_name=db_name,
                                                                                           owner=DB_USERNAME)))


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
