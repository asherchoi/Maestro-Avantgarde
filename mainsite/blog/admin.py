# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from blog.models import Post
from django.contrib import admin

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ('title','modify_date')
    list_filter = ('modify_date',)
    search_fields = ('title','content')
    prepopulated_fields = {'slug':('title',)}

admin.site.register(Post,PostAdmin)
