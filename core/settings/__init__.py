import os

# Set the default Django settings module
ENVIRONMENT = os.environ.get('DJANGO_ENV', 'local')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .local import *