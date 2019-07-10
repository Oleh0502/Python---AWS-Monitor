#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import dotenv
from django.core.management import execute_from_command_line


if __name__ == '__main__':
    dotenv.load_dotenv(dotenv.find_dotenv())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 's3bucket.settings')
    execute_from_command_line(sys.argv)
