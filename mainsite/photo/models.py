# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.core.urlresolvers import reverse
from photo.fields import ThumbnailImageField  #원본 이미지와 썸네일 이미지를 저장할수 있는 필드
from django.contrib.auth.models import User




@python_2_unicode_compatible
class Photo(models.Model):
    owner = models.ForeignKey(User,null=True)
    result_url = models.CharField(max_length=300,null=True )
    image_content = models.FileField(upload_to='photo/content_img', null=True)
    image_style = models.FileField(upload_to='photo/style_img', null=True)
    title = models.CharField('Photo Title', max_length=50)
    description = models.TextField('Photo Description', blank=True)
    upload_date = models.DateTimeField('Upload Date', auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='likes')


    class Meta:
        ordering = ['-upload_date']

    @property
    def total_likes(self):
        return self.likes.count()  # likes 컬럼의 값의 갯수를 센다

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('photo:photo_detail',args=(self.id,))

    def get_previous_post(self):
        return self.get_previous_by_modify_date()

    def get_next_post(self):
        return self.get_get_next_by_modify_date()
    
    def ssibal(self):
        z = "/"+"/".join(self.result_url.split('/')[-4:])
        print(z)
        return z

