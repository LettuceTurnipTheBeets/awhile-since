from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^aboutus/$', views.about, name='about'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^profile/settings/$', views.profile_settings, name='settings'),
    url(r'^profile/custom_category/$',
        views.custom_category, name='custom_category'),
    url(r'^profile/premade_action/$', views.premade_action, name='premade_action'),
    url(r'^profile/create_task/$', views.create_task),
    url(r'^profile/stat_init/$', views.stat_init),
    url(r'^profile/edit_task_init/$', views.edit_task_init),
    url(r'^profile/delete_task/$', views.delete_task),
    url(r'^profile/acknowledge/$', views.acknowledge),
    url(r'^profile/acknowledge_init/$', views.acknowledge_init),
    url(r'^profile/premade_action/form_category/$', views.form_category),
    url(r'^profile/premade_action/form_name/$', views.form_name),
]
