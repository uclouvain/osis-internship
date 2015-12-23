from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.middleware import RemoteUserMiddleware
import os

class ShibbollethUserBackend(RemoteUserBackend):

    def clean_username(self, username):
        return username.split("@")[0]

    def configure_user(self, user):
        return user