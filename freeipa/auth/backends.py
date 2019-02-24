import json
import requests
import logging

from pprint import pprint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

class AuthenticationBackend:
    def __init__(self):
        self.server = settings.IPA_AUTH_SERVER
        self.ssl_verify = settings.IPA_AUTH_SERVER_SSL_VERIFY
        self.ipa_version = settings.IPA_AUTH_SERVER_API_VERSION
        self.user_model = get_user_model()
        self.logger = logging.getLogger(__name__)

    def query_user_info(self, username, session):
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

        r = session.post(session_url, headers=headers, data=json.dumps(query), verify=self.ssl_verify)
        result = r.json()

        if result['error']:
            self.logger.error("[{}]: {}[code:{}]".format(result['error']['name'], result['error']['message'], result['error']['code']))
            return None

        return result['result']['result']

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
                self.logger.info('User {} attemps to login.'.format(username))
                self.logger.error(r.text)
                return None

            try:
                user = self.user_model.objects.get(username=username)
                self.logger.info('User {} logged in.'.format(username))

                if settings.IPA_AUTH_AUTO_UPDATE_USER_INFO:
                    user_info = self.query_user_info(username, s)

                    with transaction.atomic():
                        user.first_name = user_info.get('givenname', [user.first_name])[0]
                        user.last_name = user_info.get('sn', [user.last_name])[0]
                        user.email = user_info.get('mail', [user.email])[0]
                        user.save()

                        if settings.IPA_AUTH_UPDATE_USER_GROUPS:
                            for group_name in user_info['memberof_group']:
                                if not Group.objects.filter(name=group_name).exists():
                                    group = Group.objects.create(name=group_name)
                                    self.logger.info('Group {} created.'.format(group_name))
                                else:
                                    group = Group.objects.get(name=group_name)
                                user.groups.add(group)

            # User does not exists in django
            except self.user_model.DoesNotExist:
                self.logger.info('User {} does not exist.'.format(username))

                user_info = self.query_user_info(username, s)

                with transaction.atomic():
                    user = self.user_model.objects.create( username=username, 
                                                           first_name=user_info.get('givenname', [''])[0], 
                                                           last_name=user_info.get('sn', [''])[0], 
                                                           email=user_info.get('mail', [''])[0]
                                                        )

                    self.logger.info('User {} created.'.format(username))

                    if settings.IPA_AUTH_UPDATE_USER_GROUPS:
                        for group_name in user_info['memberof_group']:
                            if not Group.objects.filter(name=group_name).exists():
                                group = Group.objects.create(name=group_name)
                                self.logger.info('Group {} created.'.format(group_name))
                            else:
                                group = Group.objects.get(name=group_name)
                            user.groups.add(group)
            
        return user

    def get_user(self, user_id):
        try:
            return self.user_model.objects.get(pk=user_id)
        except self.user_model.DoesNotExist:
            return None
