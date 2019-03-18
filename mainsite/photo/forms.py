from photo.models import Photo,User

from django import forms
from django.forms.models import inlineformset_factory


PhotoInlineFormSet = inlineformset_factory(User,Photo,fields=['title','description'],extra=2)

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description','image_content', 'image_style']

class SearchForm(forms.Form):
    search_word = forms.CharField(label ='Search Word')