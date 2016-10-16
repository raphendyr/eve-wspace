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
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

userpatterns = [
    url(r'^$', views.user_edit),
    url(r'^profile/$', views.profile_admin),
    url(r'^delete/$', views.delete_user),
    url(r'^groups/$', views.user_group_list),
]

grouppatterns = [
    url(r'^$', views.group_edit),
    url(r'^profile/$', views.group_profile_admin),
    url(r'^delete/$', views.delete_group),
    url(r'^disableusers/$', views.disable_group_users),
    url(r'^enableusers/$', views.enable_group_users),
    url(r'^user/(?P<user_id>\d+)/add/$', views.add_group_user),
    url(r'^user/(?P<user_id>\d+)/remove/$', views.remove_user),
    url(r'^permissions/$', views.permissions),
]

passwordpatterns = [
    url(r'^$',
        auth_views.password_reset, name='password_reset',
        kwargs={'template_name': 'password_reset.html',
                'email_template_name': 'password_reset_email.html',
                'subject_template_name': 'reset_subject.txt',
                'post_reset_redirect': 'account:password_reset_done'}),
    url(r'^done/$',
        auth_views.password_reset_done, name='password_reset_done',
        kwargs={'template_name': 'password_reset_done.html'}),
    url(r'^(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)',
        views.password_reset_confirm, name='password_reset_confirm',
        kwargs={'template_name': 'password_reset_confirm.html',
                'post_reset_redirect': 'account:password_reset_complete'}),
    url(r'^complete/$',
        auth_views.password_reset_complete, name='password_reset_complete',
        kwargs={'template_name': 'password_reset_complete.html'}),
]

urlpatterns = [
    url(r'^login/$', auth_views.login, name='login',
        kwargs={'template_name': 'login.html'}),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^password/reset/', include(passwordpatterns)),
    url(r'^profile/$', views.edit_profile, name="profile"),
    url(r'^crest/$', views.edit_crest, name="crest"),

    url(r'^admin/user/$', views.user_admin),
    url(r'^admin/user/list/(?P<page_number>\d+)/$', views.user_list),
    url(r'^admin/group/$', views.group_admin),
    url(r'^admin/group/new/$', views.create_group),
    url(r'^admin/group/list/(?P<page_number>\d+)/$', views.group_list),
    url(r'^admin/user/new/$', views.new_user),
    url(r'^admin/user/(?P<user_id>\d+)/', include(userpatterns)),
    url(r'^admin/group/(?P<group_id>\d+)/', include(grouppatterns)),
]
