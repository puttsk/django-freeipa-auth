import requests
import json
import getpass

from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from ... import settings

class Command(BaseCommand):
    help = 'Synchronizing data with FreeIPA server'

    def add_arguments(self, parser):
        parser.add_argument('-u','--user', type=str, action='store', help='FreeIPA user')
        parser.add_argument('-p','--passwd', type=str, action='store', help='FreeIPA password', nargs='?', const='')

    def handle(self, *args, **options):
        with requests.Session() as s:
            if not options['user']: 
                ipa_username = input('Username: ')
            else:
                ipa_username = options['user']
            
            if options['passwd'] == '':
                ipa_passwd = getpass.getpass(prompt='Password:')
            else:
                ipa_passwd = options['passwd']

            ipa_url = 'https://{}/ipa/session/login_password'.format(settings.IPA_AUTH_SERVER)
            ipa_headers = { 'referer': ipa_url, 
                        'Content-Type': 'application/x-www-form-urlencoded', 
                        'Accept': 'text/plain'
                      }
            ipa_login = {'user': ipa_username, 'password': ipa_passwd}

            r = s.post(ipa_url, headers=ipa_headers, data=ipa_login, verify=settings.IPA_AUTH_SERVER_SSL_VERIFY)
            
            if r.status_code != requests.codes.ok:
                self.logger.error(r.text)
                return None

            ipa_api_url = 'https://{}/ipa'.format(settings.IPA_AUTH_SERVER)
            ipa_session_url = '{}/session/json'.format(ipa_api_url)
            ipa_headers = { 'referer': ipa_api_url, 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
            
            ipa_query = { 'id': 0, 
                          'method': 'user_find', 
                          'params': [[None], { 'all': True, 
                                               'raw': False, 
                                               'version': settings.IPA_AUTH_SERVER_API_VERSION, 
                                               'whoami': False,
                                               'no_members': False
                                            }
                                    ]
                        }
            
            r = s.post(ipa_session_url, headers=ipa_headers, data=json.dumps(ipa_query), verify=settings.IPA_AUTH_SERVER_SSL_VERIFY)
            if r.status_code != requests.codes.ok:
                print(r.text)
                exit(1)

            result = r.json()['result']

            print('user-find: Match {} users'.format(result['count']))

            UserModel = get_user_model()

            update_count = 0
            create_count = 0

            for user_info in result['result']:
                uid = user_info['uid'][0]
                user_query = UserModel.objects.filter(username=uid)

                if user_query.exists():
                    user = user_query[0]
                    print('Update user: {}.'.format(user.username))
                    
                    updated = False

                    # Update user fields 
                    for ipa_field, user_field in settings.IPA_AUTH_FIELDS_MAP.items():
                        if user_info.get(ipa_field, None): 
                            if getattr(user, user_field) != user_info[ipa_field][0]:
                                setattr(user, user_field, user_info[ipa_field][0])
                                print('  Update field {} from "{}" to "{}"'.format(user_field, getattr(user, user_field), user_info[ipa_field][0]))
                                updated = True

                    if settings.IPA_AUTH_UPDATE_USER_GROUPS:
                        user_groups = user.groups.all()
                        for group_name in user_info['memberof_group']:
                            if not Group.objects.filter(name=group_name).exists():
                                group = Group.objects.create(name=group_name)
                                print('  Group "{}" created.'.format(group_name))
                            else:
                                group = Group.objects.get(name=group_name)
                            
                            if group not in user_groups:
                                user.groups.add(group)
                                print('  Add user {} to group "{}"'.format(user.username, group))
                    
                    if updated:
                        print("User {} updated".format(user.username))
                        user.save()
                        
                        update_count += 1
                else:
                    print('Create user: {}.'.format(uid))

                    user = UserModel(username=uid)
                    # Update user fields 
                    for ipa_field, user_field in settings.IPA_AUTH_FIELDS_MAP.items():
                        if user_info.get(ipa_field, None): 
                            if getattr(user, user_field) != user_info[ipa_field][0]:
                                setattr(user, user_field, user_info[ipa_field][0])
                                print('  Set field {} to "{}"'.format(user_field, user_info[ipa_field][0]))

                    user.save()

                    if settings.IPA_AUTH_UPDATE_USER_GROUPS:
                        user_groups = user.groups.all()
                        for group_name in user_info['memberof_group']:
                            if not Group.objects.filter(name=group_name).exists():
                                group = Group.objects.create(name=group_name)
                                print('  Group "{}" created.'.format(group_name))
                            else:
                                group = Group.objects.get(name=group_name)

                            if group not in user.groups.all():
                                user.groups.add(group)
                                print('  Add user {} to group "{}"'.format(user.username, group))

                            user.groups.add(group)
                            print('  Add user {} to group "{}"'.format(user.username, group))
                        
                    print("User {} created".format(user.username))



                    create_count += 1