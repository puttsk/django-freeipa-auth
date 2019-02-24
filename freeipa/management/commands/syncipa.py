import requests
import json
import getpass
import logging

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

from ... import settings
from ... import freeipa
from ...auth.utils import update_user_info

class Command(BaseCommand):
    help = 'Synchronizing data with FreeIPA server'

    def add_arguments(self, parser):
        parser.add_argument('-u','--user', type=str, action='store', help='FreeIPA user')
        parser.add_argument('-p','--passwd', type=str, action='store', help='FreeIPA password')

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)

        with requests.Session() as s:
            ipa_username = options['user'] if options['user'] else input('Username: ')
            ipa_passwd = options['passwd'] if options['passwd'] else getpass.getpass(prompt='Password: ')
            
            r = freeipa.login(s, ipa_username, ipa_passwd)
            
            if r.status_code != requests.codes.ok:
                logger.error(r.text)
                exit(1)

            ipa_query = { 'id': 0, 
                          'method': 'user_find', 
                          'params': [[None], { 'all': True, 
                                               'raw': False, 
                                               'whoami': False,
                                               'no_members': False,
                                               'version': settings.IPA_AUTH_SERVER_API_VERSION
                                            }
                                    ]
                        }
            
            r = freeipa.query(s, ipa_query, verify_ssl=settings.IPA_AUTH_SERVER_SSL_VERIFY)

            if r.status_code != requests.codes.ok:
                logger.error(r.text)
                exit(1)

            result = r.json()['result']

            logger.info('user-find: Match {} users'.format(result['count']))

            UserModel = get_user_model()

            update_count = 0
            create_count = 0

            for user_info in result['result']:
                uid = user_info['uid'][0]
                user_query = UserModel.objects.filter(username=uid)

                if user_query.exists():
                    user = user_query[0]
                    logger.info('Found user: {}.'.format(user.username))
                    
                    if update_user_info(user, user_info, logger):
                        update_count += 1
                else:
                    logger.info('Create user: {}.'.format(uid))

                    with transaction.atomic():
                        user = UserModel.objects.create(username=uid)
                        logger.info('User {} created'.format(user.username))

                        update_user_info(user, user_info, logger)

                    create_count += 1
            
            if create_count > 0:
                logger.info('{} users created'.format(create_count))
            if update_count > 0:
                logger.info('{} users updated'.format(updated_count))