#!C:\users\andrey\documents\github\startuplab\heroku\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'gunicorn==0.14.6','console_scripts','gunicorn_django'
__requires__ = 'gunicorn==0.14.6'
import sys
from pkg_resources import load_entry_point

sys.exit(
   load_entry_point('gunicorn==0.14.6', 'console_scripts', 'gunicorn_django')()
)
