import sys
import os

INTERP = "/var/www/u3515353/data/djangoenv/bin/python"

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append('/var/www/u3515353/data/www/ani-memory.ru')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ani_album.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
