# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import Bookmark
from django.views.generic import ListView,DetailView

# Create your views here.

#---ListView
class BookmarkLV(ListView):
    model = Bookmark
    template_name = 'bookmark/bookmark_list.html'


#---DetailView
class BookmarkDV(DetailView):
    model = Bookmark


