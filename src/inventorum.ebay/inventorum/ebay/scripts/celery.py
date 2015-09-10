# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import logging
import sys

import plac
from inventorum.util.paste import boostrap_from_config


log = logging.getLogger(__name__)


def run():
    @plac.annotations(
        config_file=plac.Annotation("paster config file", 'positional', None, str),
    )
    def _run(config_file, *args):
        """
        celery entrypoint for django, using the paster config file

        ``*args`` must be kept here to allow dynamic arguments for celery in plac
        """
        boostrap_from_config(config_file)

        # filter out all arguments that have been applied by plac already
        leftover_args = [arg for arg in sys.argv if not arg in (config_file,)]
        # override ``sys.argv`` as nose or django will directly access them
        sys.argv = leftover_args

        from celery.bin.celery import main
        main(sys.argv)

    plac.call(_run)

