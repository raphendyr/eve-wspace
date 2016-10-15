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
from django.conf import settings
from django.conf.urls import include, url

import eve_sso.urls
import core.views
import account.urls
import search.urls
import Map.urls
import POS.urls
import SiteTracker.urls
import API.urls
import Alerts.urls

# Actual URL definitions
urlpatterns = [
        url(r'^$', core.views.home_view, name='index'),
        url(r'^settings/$', core.views.config_view, name='settings'),
        url(r'^evesso/', include(eve_sso.urls, namespace='eve_sso')),
        url(r'^account/', include(account.urls, namespace='account')),
        url(r'^search/', include(search.urls)),
        url(r'^map/', include(Map.urls)),
        url(r'^pos/', include(POS.urls)),
        url(r'^sitetracker/', include(SiteTracker.urls)),
        url(r'^api/', include(API.urls)),
        url(r'^alerts/', include(Alerts.urls)),
]

if settings.DEBUG:
    from django.contrib import admin
    admin.autodiscover()
    urlpatterns += [
        url(r'^admin/', include(admin.site.urls)),
    ]
