from . import dbhandler

FUSIONPBX_DB = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'fusionpbx',
    'USER': 'fusionpbx',
    'PASSWORD': '',
    'HOST': '127.0.0.1',
    'PORT': '5432',
}

FUSIONPBX_ESL = {
    'IP': '127.0.0.1',
    'PORT': '8021',
    'SECRET': 'ClueCon',
}