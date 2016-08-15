import os
import site
import sys

sys.stdout = sys.stderr

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
