# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import os
import logging
import subprocess

from inventorum.util.paste import boostrap_from_config

import plac

log = logging.getLogger(__name__)


def _db_provision(db_name, with_drop):
    from django.conf import settings

    sandbox_root = settings.BUILDOUT_ROOT
    log.debug("sandbox root is %s", sandbox_root)
    sandbox_exec_path = os.path.join(sandbox_root, "parts", "postgresql", "bin")

    db = settings.DATABASES["default"]
    DB_HOST = db["HOST"]
    DB_USERNAME = db["USER"]

    log.info("running in sandbox mode")

    connect_options = [
        "--host={host}".format(host=DB_HOST)
    ]

    psql = [os.path.join(sandbox_exec_path, "psql")] + connect_options

    createdb = [os.path.join(sandbox_exec_path, "createdb"), "--owner=%s" % DB_USERNAME] + connect_options
    createdb = createdb + [
        "--template=template0", "--encoding=UTF8",
        "--locale=en_US.UTF-8",
        "'{db_name}'".format(db_name=db_name)
    ]

    dropdb = [os.path.join(sandbox_exec_path, "dropdb")] + connect_options
    dropdb = dropdb + ["'{db_name}'".format(db_name=db_name)]

    log.debug(" ".join(createdb))
    log.debug(" ".join(dropdb))

    proc = subprocess.Popen(" ".join(createdb), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    _out, _err = proc.communicate()
    if _err:
        if with_drop:
            proc = subprocess.Popen(" ".join(dropdb), stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True)
            _out, _err = proc.communicate()
            if not _err:
                log.info("database '%s' dropped." % db_name)
            else:
                log.error("could not drop db '%s': %s", db_name, _err)
                exit(1)

            proc = subprocess.Popen(" ".join(createdb), stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True)
            _out, _err = proc.communicate()
            if not _err:
                log.info("database '%s' created.", db_name)
            else:
                log.error("could not create db '%s': %s", db_name, _err)
                exit(1)
        else:
            log.error(_err)
            exit(1)
    else:
        log.info("database '%s' created." % db_name)


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
