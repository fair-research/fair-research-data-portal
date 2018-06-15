# FAIR Research Data Portal


This is a portal which provides a very thin wrapper around Django Globus
Portal Framework.

## Installation

### Locally
Clone and install the App locally:

```
    $ git clone https://github.com/fair-research/fair-research-data-portal
    $ cd fair-research-data-portal.git
    $ pipenv install -r requirements.txt
    $ pipenv shell
```

Create a Globus App at [developers.globus.org](https://developers.globus.org)
and add the keys to your local config file below:

portal/local_settings.py
```
from django.conf import settings
DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = 'thing you generate with `openssl rand -hex 32`'
SOCIAL_AUTH_GLOBUS_SECRET = 'find at developers.globus.org'
settings.LOGGING['handlers']['stream']['level'] = 'DEBUG'
```

Now just run migrations, and start the server

```
    $ python manage.py migrate
    $ python manage.py runserver
```

The app will be running locally at `http://localhost:8000`

### On a server

This app is intended to be run through WSGI. Static files can be copied
to a location your favorite webserver can serve them through:

    $ python manage.py collectstatic

Configure the filesystem location where files should be collected with
`settings.STATIC_ROOT` and the URL this webapp should expect them with
`settings.STATIC_URL`.
