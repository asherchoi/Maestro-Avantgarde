# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import ListView,DetailView
from photo.models import Photo
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.core.urlresolvers import reverse_lazy,reverse
from mainsite.views import LoginRequiredMixin
from django.views.generic.edit import FormView
from photo.forms import SearchForm, PhotoForm
from photo.service_app import StyleTransfer
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse

try:
    from django.utils import simplejson as json
except ImportError:
    import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
@require_POST
def like(request):

    if request.method == 'POST':
        user = request.user # 로그인한 유저를 가져온다.
        result_id = request.POST.get('pk', None)
        result = Photo.objects.get(pk = result_id) #해당 메모 오브젝트를 가져온다.

        if result.likes.filter(id = user.id).exists(): #이미 해당 유저가 likes컬럼에 존재하면
            result.likes.remove(user) #likes 컬럼에서 해당 유저를 지운다.
            message = 'You disliked this'
        else:
            result.likes.add(user)
            message = 'You liked this'

    context = {'likes_count' : result.total_likes, 'message' : message}
    return HttpResponse(json.dumps(context), content_type='application/json')
    # dic 형식을 json 형식으로 바꾸어 전달한다.


class PhotoDV(DetailView):
    model = Photo

class PhotoLV(ListView):
    model = Photo
    paginate_by = 8

class PhotoMyLV(LoginRequiredMixin,ListView):
    model = Photo
    template_name = 'photo/photo_Mylist.html'
    paginate_by = 8


def photoCreate(request):

    if not request.user.is_authenticated():
        context = {'form': AuthenticationForm}
        return render(request, 'registration/login.html',context)
    else:
        if request.method == "POST":
            form = PhotoForm(request.POST, request.FILES)
            if form.is_valid():
                photo = form.save(commit = False)
                photo.owner = request.user
                photo.title = form.instance.title
                photo.description = form.instance.description
                photo.image_content = form.instance.image_content
                photo.image_style = form.instance.image_style
                result_url = ""

                photo.save()
                print(photo.image_content.path)
                
                print("-----------")
                print(photo.image_content.path.split('/'))
                z = photo.image_content.path.split('/')[:-2]
                print(z)
                print("-----------")
                z.extend(['result_img', photo.image_content.url.split('/')[-1].split('.')[0] + photo.image_style.url.split('/')[-1]])
                print(z)
                result_url_1 = "/"+"/".join(z[-2:])
                print(photo.image_content.path)
                temp = photo.image_content.path.split('/')[:-2]
                print(temp)
                result_url = "/".join(temp)+result_url_1
                print("sex:",result_url)

                Photo.objects.filter(id = photo.id).update(result_url = result_url)
                ssibal = Photo.objects.get(id = photo.id)
                result = StyleTransfer(photo.image_content.path, photo.image_style.path, ssibal.result_url)
                result.transfer()
                del result

                return HttpResponseRedirect(reverse('photo:photo_Mylist'))
        else:
            form = PhotoForm()
        context = {'form':form}
        return render(request, 'photo/photo_form.html', context)


class PhotoCreateView(LoginRequiredMixin,CreateView,ListView):
    model = Photo
    tempResult_url = ""
    fields = ['title','description','image_content','image_style']

    #success_url = reverse_lazy('photo:sex',args ="ssibal"))

    def form_valid(self, form):
        #print(self.request.user)  #--jungsangsu
        #print(self.request.FILES) # -- dict 형태로

        form.instance.owner = self.request.user
        print(form.instance.image_content.url)
        print(form.instance.image_style.url)


        form.instance.result_url = form.instance.image_content.url[0:-4]+form.instance.image_style.url[7:]

        #form.instance.result_url = self.request.FILES
        tempResult_url = form.instance.result_url
        return super(PhotoCreateView, self).form_valid(form)

class PhotoChangeLV(LoginRequiredMixin,ListView):
    #model = Photo
    template_name = 'photo/photo_change_list.html'

    def get_queryset(self):
        return Photo.objects.filter(owner=self.request.user)

class PhotoUpdateView(LoginRequiredMixin, UpdateView):
    model = Photo
    fields = ['title','description']
    success_url = reverse_lazy('photo:index')

class PhotoDeleteView(LoginRequiredMixin, DeleteView):
    model = Photo
    success_url = reverse_lazy('photo:index')




#--- FormView
class SearchFormView(FormView):
    form_class = SearchForm
    template_name = 'photo/photo_search.html'

    def form_valid(self, form):
        schWord = '%s' % self.request.POST['search_word']
        photo_list = Photo.objects.filter(Q(title__icontains=schWord)).distinct()

        context = {}
        context['form'] = form
        context['search_term'] = schWord
        context['object_list'] = photo_list

        return render(self.request, self.template_name, context)
