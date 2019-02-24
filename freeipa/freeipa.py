import requests
import json

from . import settings

def login(session, ipa_username, ipa_passwd, server=settings.IPA_AUTH_SERVER, verify_ssl=settings.IPA_AUTH_SERVER_SSL_VERIFY):
    """Login to FreeIPA server 

    Args:
        session (requests.Session()): object containing session to store FreeIPA cookies.
        ipa_username (str): FreeIPA username
        ipa_password (str): FreeIPA password
        server (str): FreeIPA server url (default: settings.IPA_AUTH_SERVER)
        verify_ssl (boolean): Verify the server’s TLS certificate (default: settings.IPA_AUTH_SERVER_SSL_VERIFY)

    Returns:
        requests.Response() object containing login results

    """

    ipa_url = 'https://{}/ipa/session/login_password'.format(server)
    ipa_headers = { 'referer': ipa_url, 
                    'Content-Type': 'application/x-www-form-urlencoded', 
                    'Accept': 'text/plain'
                    }
    ipa_login = {'user': ipa_username, 'password': ipa_passwd}

    return session.post(ipa_url, headers=ipa_headers, data=ipa_login, verify=verify_ssl)

def query(session, data, server=settings.IPA_AUTH_SERVER, verify_ssl=settings.IPA_AUTH_SERVER_SSL_VERIFY):
    """Call FreeIPA API

    Args:
        session (requests.Session()): object containing session to store FreeIPA cookies.
        data (json): dict or json string containing FreeIPA request
        server (str): FreeIPA server url (default: settings.IPA_AUTH_SERVER)
        verify_ssl (boolean): Verify the server’s TLS certificate (default: settings.IPA_AUTH_SERVER_SSL_VERIFY)

    Returns:
        requests.Response() object containing request results

    """
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
    """Show information of a FreeIPA user

    Args:
        session (requests.Session()): object containing session to store FreeIPA cookies.
        username (str): username of a user to query information
        server (str): FreeIPA server url (default: settings.IPA_AUTH_SERVER)
        verify_ssl (boolean): Verify the server’s TLS certificate (default: settings.IPA_AUTH_SERVER_SSL_VERIFY)
        version (str): FreeIPA server API version (default: settings.IPA_AUTH_SERVER_API_VERSION)
        logger (logging.Logger): logger to log results. 

    Returns:
        dict containing user information

    """

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