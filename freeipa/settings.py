from django.conf import settings

__default_user_map = { 'givenname': 'first_name',
                       'sn'       : 'last_name',
                       'mail'     : 'email',
                     }

IPA_AUTH_SERVER = getattr(settings, 'IPA_AUTH_SERVER', None)
IPA_AUTH_SERVER_SSL_VERIFY = getattr(settings, 'IPA_AUTH_SERVER_SSL_VERIFY', True)
IPA_AUTH_SERVER_API_VERSION = getattr(settings, 'IPA_AUTH_SERVER_API_VERSION', '2.230')
IPA_AUTH_AUTO_UPDATE_USER_INFO = getattr(settings, 'IPA_AUTH_AUTO_UPDATE_USER_INFO', True)
IPA_AUTH_UPDATE_USER_GROUPS = getattr(settings, 'IPA_AUTH_UPDATE_USER_GROUPS', True)

# Dictionary mapping FreeIPA field to Django user attribytes
IPA_AUTH_FIELDS_MAP = getattr(settings, 'IPA_AUTH_FIELDS_MAP', __default_user_map)