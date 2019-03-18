# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from photo.models import Photo
# from photo.models import Gallery
# Register your models here.
class PhotoInline(admin.StackedInline):
    model = Photo
    extra = 2

# class GalleryAdmin(admin.ModelAdmin):
#     inlines = [PhotoInline]
#     list_display = ('name', 'description')

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title','upload_date')

# class PhotoContentAdmin(admin.ModelAdmin):
#     list_display = ('title','upload_date')
#
# class PhotoStyleAdmin(admin.ModelAdmin):
#     list_display = ('title','upload_date')


# admin.site.register(Gallery,GalleryAdmin)
admin.site.register(Photo,PhotoAdmin)
# admin.site.register(PhotoContent,PhotoContentAdmin)
# admin.site.register(PhotoStyle,PhotoStyleAdmin)