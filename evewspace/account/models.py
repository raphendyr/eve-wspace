#   Eve W-Space
#   Copyright 2014 Andrew Austin and contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import pytz
import datetime
import time

from django import forms
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.cache import cache
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.core.mail import send_mail

from Map.models import Map, System

User = settings.AUTH_USER_MODEL

class EWSUserManager(BaseUserManager):

    def _create_user(self, username, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, True, True,
                                 **extra_fields)

class EWSUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'))
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    defaultmap = models.ForeignKey(Map, related_name = "defaultusers", blank=True, null=True)
    objects = EWSUserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        permissions = (('account_admin', 'Administer users and groups'),)

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    @cached_property
    def _eve_auth(self):
        """shortcut to python-social-auth's EVE-related extra data for this user"""
        return self.social_auth.get(provider='eveonline').extra_data

    def _get_crest_tokens(self):
        """get tokens for authenticated CREST"""
        expires_in = time.mktime(
            dateutil.parser.parse(
                self._eve_auth['expires']  # expiration time string
            ).timetuple()                  # expiration timestamp
        ) - time.time()                    # seconds until expiration
        return {
            'access_token': self._eve_auth['access_token'],
            'refresh_token': self._eve_auth['refresh_token'],
            'expires_in': expires_in
        }

    @property
    def character_id(self):
        """get CharacterID from authentification data"""
        return self._eve_auth['id']

    def get_portrait_url(self, size=128):
        """returns URL to Character portrait from EVE Image Server"""
        return "https://image.eveonline.com/Character/{0}_{1}.jpg".format(self.character_id, size)


    def update_location(self, sys_id, charid, charname, shipname, shiptype):
        """
        Updates the cached locations dict for this user.
        """
        current_time = time.time()
        user_cache_key = 'user_%s_locations' % self.pk
        user_locations_dict = cache.get(user_cache_key)
        time_threshold = current_time - (60 * 15)
        location_tuple = (sys_id, charname, shipname, shiptype, current_time)
        if user_locations_dict:
            user_locations_dict.pop(charid, None)
            user_locations_dict[charid] = location_tuple
        else:
            user_locations_dict = {charid: location_tuple}
        # Prune dict to ensure we're not carrying over stale entries
        for charid, location in user_locations_dict.items():
            if location[4] < time_threshold:
                user_locations_dict.pop(charid, None)

        cache.set(user_cache_key, user_locations_dict, 60 * 15)
        return user_locations_dict

    def get_settings(self):
        from core.utils import get_config
        from core.models import ConfigEntry
        config_dict = dict()
        for x in ConfigEntry.objects.filter(user=None).all():
            config_dict[x.name] = get_config(x.name, self).value
        return config_dict


class GroupProfile(models.Model):
    """GroupProfile defines custom fields tied to each Group record."""
    group = models.OneToOneField(Group, related_name='profile')
    description = models.CharField(max_length=200, blank=True, null=True)
    regcode = models.CharField(max_length=64, blank=True, null=True)
    visible = models.BooleanField(default=True)


def create_group_profile(sender, instance, created, **kwargs):
    """Handle group creation event and create a new group profile."""
    if created:
        GroupProfile.objects.create(group=instance)

post_save.connect(create_group_profile, sender=Group)


class EWSUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=30, label=_("Username"))
    class Meta:
        model = EWSUser
        fields = ('username',)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            EWSUser.objects.get(username=username)
        except EWSUser.DoesNotExist:
            return username
        raise forms.ValidationError(
                self.error_messages['duplicate_username'],
                code='duplicate_username',
                )


class EWSUserChangeForm(UserChangeForm):
    class Meta:
        model = EWSUser
        fields = ('username','email','password','is_active')


class RegistrationForm(EWSUserCreationForm):
    """Extends the django registration form to add fields."""
    username = forms.CharField(max_length=30, label="Username")
    email = forms.EmailField(required=False, label="E-Mail Address (Optional)")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password:")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password:")
    regcode = forms.CharField(max_length=64, label="Registration Code")
    
    email.widget.attrs['class'] = 'form-control input-sm'
    username.widget.attrs['class'] = 'form-control input-sm'
    password1.widget.attrs['class'] = 'form-control input-sm'
    password2.widget.attrs['class'] = 'form-control input-sm'
    regcode.widget.attrs['class'] = 'form-control input-sm'

