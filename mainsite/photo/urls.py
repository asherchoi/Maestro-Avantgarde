"""mainsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from photo.views import *
from . import views

urlpatterns = [

    #--------------------------------photo---------------------------------------------
    # #Example : /
    url(r'^$',PhotoLV.as_view(),name='index'),

    # #Example : /gallery/,
    url(r'^gallery/$',PhotoLV.as_view(), name='photo_list'),

    # #Example : /Mygallery/,
    url(r'^Mygallery/$', PhotoMyLV.as_view(), name='photo_Mylist'),

    # Example : /photo/99/
    url(r'^photo/(?P<pk>\d+)/$', PhotoDV.as_view(), name='photo_detail'),

    #Example: /photo/add/
    #url(r'^photo/add/$',PhotoCreateView.as_view(),name="photo_add",),

    #Example: /photo/change/
    url(r'^photo/change/$',PhotoChangeLV.as_view(), name="photo_change",),

    #Example: /photo/update/
    url(r'^photo/(?P<pk>[0-9]+)/update/$',PhotoUpdateView.as_view(), name="photo_update",),

    #Example:/photo/99/delete/
    url(r'^photo/(?P<pk>[0-9]+)/delete/$',PhotoDeleteView.as_view(), name="photo_delete",),

    # Example: /search/
    url(r'^search/$', SearchFormView.as_view(), name='search'),

    url(r'^photo/add/$', views.photoCreate, name = 'photo_create'),

    url(r'^like/$', views.like, name='like'),
]


