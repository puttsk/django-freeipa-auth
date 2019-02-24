import requests
import json

from . import settings

def login(session, ipa_username, ipa_passwd, server=settings.IPA_AUTH_SERVER, verify_ssl=settings.IPA_AUTH_SERVER_SSL_VERIFY):
    ipa_url = 'https://{}/ipa/session/login_password'.format(server)
    ipa_headers = { 'referer': ipa_url, 
                    'Content-Type': 'application/x-www-form-urlencoded', 
                    'Accept': 'text/plain'
                    }
    ipa_login = {'user': ipa_username, 'password': ipa_passwd}

    return session.post(ipa_url, headers=ipa_headers, data=ipa_login, verify=verify_ssl)

def query(session, data, server=settings.IPA_AUTH_SERVER, verify_ssl=settings.IPA_AUTH_SERVER_SSL_VERIFY):
    ipa_api_url = 'https://{}/ipa'.format(server)
    ipa_session_url = '{}/session/json'.format(ipa_api_url)
    ipa_headers = { 'referer': ipa_api_url, 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                    }

    if not type(data) is str:
        data = json.dumps(data)

    return session.post(ipa_session_url, headers=ipa_headers, data=data, verify=verify_ssl)

def query_user_info( session, 
                     username, 
                     server=settings.IPA_AUTH_SERVER, 
                     verify_ssl=settings.IPA_AUTH_SERVER_SSL_VERIFY, 
                     version=settings.IPA_AUTH_SERVER_API_VERSION,
                     logger=None
                   ):

    data = { 'id': 0, 
                'method': 'user_show', 
                'params': [[username], {'all': True, 'raw': False, 'version': version}]
           }

    r = query(session, data, server=server, verify_ssl=verify_ssl)
    result = r.json()

    if result['error']:
        if logger:
            logger.error("[{}]: {}[code:{}]".format(result['error']['name'], result['error']['message'], result['error']['code']))
        else:
            raise ValueError("[{}]: {}[code:{}]".format(result['error']['name'], result['error']['message'], result['error']['code']))

        return None

    return result['result']['result']