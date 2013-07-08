# Django settings for OpenMalaria project.
import os
import django.template
django.template.add_to_builtins('django.templatetags.future')


# Debug setttings. These should be turned off for production environments
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# get the project path to allow relative paths
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(PROJECT_PATH, os.pardir)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Define the database settings to use with the site.
# A valid definition is required for the site to function correctly
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'data.db',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

VERSION_ID = "1.0"

# Define BOINC parameters.
# A valid definition is required for the site to function correctly
# BOINC server host (full url to php script)
BOINC_HOST = 'URL'   #Cleared out
# Credentials for connecting to the BOINC server
BOINC_USER = 'USER'                             #Cleared out
BOINC_PASSWORD = 'PASSORD'                          #Celaredd out

#URL to the RabbitMQ server which distributes the jobs to the computational nodes.
# A valid definition is required for the site to function correctly
CELERY_BROKER = "amqp://guest:guest@DOMAIN:5672"

# Email messaging parameters so that password reset emails can be sent out, etc.
# A valid definition is required for the site to function correctly
EMAIL_HOST = 'smtp.domain.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'email@domain.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'email@domain.com'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT =''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'static') ,
)

LOGIN_URL = '/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '#19_=9&amp;qvqn20t7##fnkr@vd7f_yywyh5e4(u+)1dx#x3%v(^x'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #This should be uncommented (in addition to the HTTPS support below) to force all communication across secure http
    #'frontend.secureMiddleware.SecureRequiredMiddleware', #Added to force index to secure url
)

#These should be turned on by default to force all communication across secure http (in addition to the SecureMiddleware above)
#HTTPS_SUPPORT = True
#SECURE_REQUIRED_PATHS = (
#    '/',
#)


# Brings user to the login screen when hitting the root of the server
LOGIN_URL = '/'

# Defines site URLs
ROOT_URLCONF = 'OpenMalaria.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'OpenMalaria.wsgi.application'

# Define where html templates are
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, 'templates'),)

TEMPLATE_CONTEXT_PROCESSORS =  ("django.contrib.auth.context_processors.auth",
                                "django.core.context_processors.debug",
                                "django.core.context_processors.i18n",
                                "django.core.context_processors.media",
                                "django.core.context_processors.static",
                                "django.core.context_processors.tz",
                                "django.contrib.messages.context_processors.messages",
                                'django.core.context_processors.request')

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'frontend'
)

SESSION_COOKIE_AGE = 7200
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
