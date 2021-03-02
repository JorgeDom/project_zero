import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('c:/users/jorged/appdata/local/programs/python/python37/lib/site-packagess')

# Add the app's directory to the PYTHONPATH
sys.path.append('C:/GitHub/EasyStock')
#sys.path.append('C:/GitHub/EasyStock/EasyStock')

os.environ['DJANGO_SETTINGS_MODULE'] = 'EasyStock.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EasyStock.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()