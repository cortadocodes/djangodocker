"""
Django settings for djangodocker project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import logging
import sys
from typing import Union, Iterable

import requests
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

def get_env_var(name, required=True, except_commands: Iterable[str]=None) \
        -> Union[str, None]:
    """
    Gets an environment variable, raising an error if required. Will return a
    None if not required, or if Django was started with one of the
    'except_commands', collectstatic by default

    :param name: The name of the environment variable
    :param required: If the env var is undefined, should the function return
                     None or raise an error?
    :param except_commands: If Django is started with one of these commands,
                     required variables that were not find in the environment
                     will still not raise an error. Otherwise a placeholder is
                     returned
    :return: str or None
    """

    if except_commands is None:
        except_commands = ['collectstatic']

    var = os.environ.get(name)

    if required and var is None:
        ignore = set(except_commands)
        matching_commands = ignore.intersection(sys.argv)
        if not matching_commands:
            raise KeyError(f"Environment variable {name} if not defined")
        else:
            logger.info(f"Required environment variable {name} was ignored, "
                        f"as Django was started with {matching_commands}")
            return "PLACEHOLDER"

    return var


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
_debug = get_env_var('DEBUG', required=False)
DEBUG = _debug == '1'  # only switch on debug if the DEBUG env var is '1'

ALLOWED_HOSTS = get_env_var('HOST')

# We're taking the 'real' ALLOWED_HOST from the environment
# Yet to make sure we're passing the ELB health check, we need to
# Add the hosting EC2 instance's private IP here. If we're on AWS,
# that is.

# Use the Instance Metadata API to get our private IP
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html
try:
    r = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4',
                     timeout=0.5)
    ALLOWED_HOSTS.append(r.text)
except ConnectionError:
    logger.warning("Could not obtain EC2 metadata")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangodocker'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangodocker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangodocker.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_var('DB_NAME'),
        'USER': get_env_var('DB_USER'),
        'PASSWORD': get_env_var('DB_PASSWORD'),
        'HOST': get_env_var('DB_HOST')
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/static'

# The default redirect URL from the login route
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/login/'
