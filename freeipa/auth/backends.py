import json
import requests
import logging

from pprint import pprint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class AuthenticationBackend:
    def __init__(self):
        self.server = settings.IPA_SERVER
        self.ssl_verify = settings.IPA_SERVER_SSL_VERIFY
        self.ipa_version = settings.IPA_SERVER_API_VERSION
        self.user_model = get_user_model()
        self.logger = logging.getLogger(__name__ + ".AuthenticationBackend")

    def authenticate(self, request, username=None, password=None):
        user = None

        with requests.Session() as s:
            ipa_url = 'https://{}/ipa/session/login_password'.format(self.server)
            headers = { 'referer': ipa_url, 
                        'Content-Type': 'application/x-www-form-urlencoded', 
                        'Accept': 'text/plain'
                      }
            login = {'user': username, 'password': password}

            r = s.post(ipa_url, headers=headers, data=login, verify=self.ssl_verify)
            
            if r.status_code != requests.codes.ok:
                self.logger.warning('User {} attemps to login.'.format(username))
                return None

            try:
                user = self.user_model.objects.get(username=username)
                self.logger.warning('User {} logged in.'.format(username))

            except self.user_model.DoesNotExist:
                self.logger.warning('User {} does not exist.'.format(username))
                ipa_api_url = 'https://{}/ipa'.format(self.server)
                session_url = '{}/session/json'.format(ipa_api_url)
                headers = { 'referer': ipa_api_url, 
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                          }
                
                query = { 'id': 0, 
                          'method': 'user_show', 
                          'params': [[username], {'all': True, 'raw': False, 'version': self.ipa_version}]
                        }

                r = s.post(session_url, headers=headers, data=json.dumps(query), verify=self.ssl_verify)
                result = r.json()

                if result['error']:
                    self.logger.error("[{}]: {}[code:{}]".format(result['error']['name'], result['error']['message'], result['error']['code']))
                    return None

                user_info = result['result']['result']
                user = self.user_model.objects.create(username=username, first_name=user_info['givenname'][0], last_name=user_info['sn'][0], email=user_info['mail'][0])
                self.logger.warning('User {} created.'.format(username))

                for group_name in user_info['memberof_group']:
                    if not Group.objects.filter(name=group_name).exists():
                        group = Group.objects.create(name=group_name)
                        self.logger.warning('Group {} created.'.format(group_name))
                    else:
                        group = Group.objects.get(name=group_name)
                    user.groups.add(group)

                return user
            
        return user

    def get_user(self, user_id):
        try:
            return self.user_model.objects.get(pk=user_id)
        except self.user_model.DoesNotExist:
            return None
