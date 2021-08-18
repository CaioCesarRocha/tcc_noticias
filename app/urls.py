from django.conf.urls import url

from . import views

from django.urls import path, include

urlpatterns = [
    url('url_base/get', views.get_url_base, name='get_notices'),
    url('url_base/post', views.post_rating, name='post_rating'),
]