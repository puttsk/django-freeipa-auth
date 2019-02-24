from .. import settings

from django.db import transaction
from django.contrib.auth.models import Group

@transaction.atomic
def update_user_info(user, user_info, logger):
    updated = False

    # Update user fields 
    for ipa_field, user_field in settings.IPA_AUTH_FIELDS_MAP.items():
        if user_info.get(ipa_field, None): 
            if getattr(user, user_field) != user_info[ipa_field][0]:
                logger.info('  Update field {} from "{}" to "{}"'.format(user_field, getattr(user, user_field), user_info[ipa_field][0]))
                setattr(user, user_field, user_info[ipa_field][0])
                updated = True

    if settings.IPA_AUTH_UPDATE_USER_GROUPS:
        user_groups = user.groups.all()
        for group_name in user_info['memberof_group']:
            if not Group.objects.filter(name=group_name).exists():
                group = Group.objects.create(name=group_name)
                logger.info('  Group "{}" created.'.format(group_name))
            else:
                group = Group.objects.get(name=group_name)
            
            if group not in user_groups:
                user.groups.add(group)
                logger.info('  Add user {} to group "{}"'.format(user.username, group))
    
    if updated:
        logger.info("User {} updated".format(user.username))
        user.save()
    
    return updated