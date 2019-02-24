django-freeipa-auth
====================

`django-freeipa-auth` provides a Django backend authentication app for FreeIPA authentication. The app uses FreeIPA JSON API for its operation. 

Quick start
------------

1. Install using `pip`

```
pip install django-freeipa-auth-json
```

2. Add `freeipa` to `INSTALLED_APPS` in the settings file.

```python
INSTALLED_APPS = [
    ...
    'freeipa',
]
```

3. Add `freeipa.auth.backends.AuthenticationBackend` to `AUTHENTICATION_BACKENDS` in the settings file.

```python
AUTHENTICATION_BACKENDS = [
    ...
    'freeipa.auth.backends.AuthenticationBackend',
]
```

4. Add following settings to the setting files

```python
# REQUIRED: 
IPA_AUTH_SERVER = 'ipa.demo1.freeipa.org'

# OPTIONAL:
IPA_AUTH_SERVER_SSL_VERIFY = True
IPA_AUTH_SERVER_API_VERSION = '2.230'
# Automatically update user information when logged in
IPA_AUTH_AUTO_UPDATE_USER_INFO = True  
# Automatically create and update user groups.
IPA_AUTH_UPDATE_USER_GROUPS = True 

# Dictionary mapping FreeIPA field to Django user attributes
IPA_AUTH_FIELDS_MAP = { 'givenname': 'first_name',
                        'sn'       : 'last_name',
                        'mail'     : 'email',
                      }
```

Command Line
--------------

`django-freeipa-auth` provide `syncipa` command to import and update users stored in Django database with FreeIPA server.

```
usage: manage.py syncipa [-h] [-u USER] [-p PASSWD] 

Synchronizing data with FreeIPA server

optional arguments:
  -h, --help                  show this help message and exit

login arguments: require a user with permission to query all users (e.g. administrator.)
  -u USER, --user USER
  -p PASSWD, --passwd PASSWD  
```
