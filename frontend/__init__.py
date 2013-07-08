#from django.db.models.signals import post_syncdb
#from django.contrib.auth.models import Group, Permission
#import models

#def create_group_permissions(sender, **kwargs):
#    print ('Creating groups')
#    grp, created = Group.objects.get_or_create(name='account_creator')
#    if created:
#        grp.save()

#        print('Account Creator Group added')


#    pass

#post_syncdb.connect(create_group_permissions, sender=models)
