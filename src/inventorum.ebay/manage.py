#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    env = os.environ.get('INV_ENV', 'development' if 'test' not in sys.argv else 'test')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventorum.ebay.settings." + env)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
