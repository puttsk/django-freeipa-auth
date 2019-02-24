import requests
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .. import settings
from .. import freeipa
from .utils import update_user_info

class AuthenticationBackend:
    def __init__(self):
        self.server = settings.IPA_AUTH_SERVER
        self.ssl_verify = settings.IPA_AUTH_SERVER_SSL_VERIFY
        self.ipa_version = settings.IPA_AUTH_SERVER_API_VERSION
        self.user_model = get_user_model()
        self.logger = logging.getLogger(__name__)

    def authenticate(self, request, username=None, password=None):
        user = None

        with requests.Session() as s:
            r = freeipa.login(s, username, password, server=self.server, verify_ssl=self.ssl_verify)
            
            if r.status_code != requests.codes.ok:
                self.logger.info('User {} attemps to login.'.format(username))
                self.logger.error(r.text)
                return None

            # Check if user exists in Django database 
            # If user exists, return user object. Updating user if IPA_AUTH_AUTO_UPDATE_USER_INFO is set. 
            # If not, create a new user. 
            try:
                user = self.user_model.objects.get(username=username)
                self.logger.info('User {} logged in.'.format(username))

                if settings.IPA_AUTH_AUTO_UPDATE_USER_INFO:
                    user_info = freeipa.query_user_info(s, username, logger=self.logger)
                    update_user_info(user, user_info, self.logger)
                    
            except self.user_model.DoesNotExist:
                self.logger.info('User {} does not exist.'.format(username))

                user_info = freeipa.query_user_info(s, username, logger=self.logger)
                user = self.user_model.objects.create(username=username)
                self.logger.info('User {} created.'.format(username))

                update_user_info(user, user_info, self.logger)
        
        return user

    def get_user(self, user_id):
        try:
            return self.user_model.objects.get(pk=user_id)
        except self.user_model.DoesNotExist:
            return None
