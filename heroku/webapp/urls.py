from django.conf.urls import patterns, include, url
import webapp.views as views
from webapp.settings import DEBUG
from django.contrib import admin
admin.autodiscover()

# Custom Routes
urlpatterns = patterns('',
    (r'^$', views.index),
    (r'^/$', views.index),
    (r'^index/$', views.index),

    (r'^user/(?P<username>.*)$', views.profile),
    (r'^signup/$', views.signup),
    (r'^signin/$', views.signin),
    (r'^signout/$', views.signout),

    (r'^feed/$', views.feed),
    (r'^post/$', views.newbid),
    (r'^querybids/$', views.querybids),
    (r'^alltags/$', views.alltags),

    (r'^questions/(?P<bidID>.*)$', views.single_bid_page),
    (r'^questions/(?P<bidID>.*)$/(?P<userID>.*)$', views.single_interaction_page),
)

if DEBUG:
    urlpatterns += patterns('',
        (r'^credit/$', views.credit_test),
    )

# Admin
urlpatterns += patterns(
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
