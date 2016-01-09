"""
Utility file for Tests units
"""
from django.contrib.auth.models import User

__author__ = 'glamarca'

ADMIN_USER='admin_user'
GRANTED_USER='granted_user'
VALID_USER='valid_user'
INVALID_USER='invalid_user'
PASSWORD='password'
EMAIL='user@osis.org'

def init_admin_user():
    """
    Initialise an Admin user
    """
    user = User.objects.create_superuser(ADMIN_USER,EMAIL,PASSWORD,is_staff=True)
    user.save()

def init__granted_user() :
    """
    Initialise a user tha has been granted to acces tested methods.
    If a new authorisation is set for a tested method , it has to be added to the "set_permissions_to_granted" methods.
    """
    user = User.objects.create_user(GRANTED_USER,EMAIL,PASSWORD)
    set_permissions_to_granted(user)
    user.save()

def set_permissions_to_granted(user):
    """
    Grant permissions to the user
    :param user: The user to grant permissions
    """
    return

def init_valid_user():
    """
    Initialise a user that can log in , but doesn't have authorisations to access methods
    """
    user = User.objects.create_user(VALID_USER,EMAIL,PASSWORD)
    user.save()

def init_all_test_users() :
    """
    Initialise all user types
    """
    init_admin_user()
    init__granted_user()
    init_valid_user()

