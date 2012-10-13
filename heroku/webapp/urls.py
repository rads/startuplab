from django.conf.urls import patterns, include, url
import webapp.views as views


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', views.index),
    (r'^/$', views.index),
    (r'^index/$', views.index),

    (r'^signup/$', views.signup),
    (r'^signin/$', views.signin),
    (r'^signout/$', views.signout),

    (r'^feed/$', views.feed),
    (r'^post/$', views.post),
    
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
