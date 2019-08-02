# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import ListView,DetailView
from photo.models import Photo
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy,reverse
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
from threading import Timer
from threading import Lock

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
                z = photo.image_content.path.split('/')[:-2]
                z.extend(['result_img', photo.image_content.url.split('/')[-1].split('.')[0] + photo.image_style.url.split('/')[-1]])
                result_url_1 = "/"+"/".join(z[-2:])
                temp = photo.image_content.path.split('/')[:-2]
                result_url = "/".join(temp)+result_url_1
                Photo.objects.filter(id = photo.id).update(result_url = result_url)
                t = StyleTransfer(photo.image_content.path[:], photo.image_style.path[:], Photo.objects.get(id = photo.id).result_url[:])
                t.transfer()
                #queue.append(StyleTransfer(photo.image_content.path[:], photo.image_style.path[:], Photo.objects.get(id = photo.id).result_url[:]))
                return HttpResponseRedirect(reverse('photo:photo_Mylist'))
        else:
            form = PhotoForm()
        context = {'form':form}
        return render(request, 'photo/photo_form.html', context)
'''
queue = []
lock = Lock()

def work():
    if queue:
        with lock:
            task_instance = queue.pop(0)
        task_instance.transfer()
        del task_instance
    Timer(5, work).start()

work()
'''
class PhotoCreateView(LoginRequiredMixin,CreateView,ListView):
    model = Photo
    tempResult_url = ""
    fields = ['title','description','image_content','image_style']
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.result_url = form.instance.image_content.url[0:-4]+form.instance.image_style.url[7:]
        tempResult_url = form.instance.result_url
        return super(PhotoCreateView, self).form_valid(form)

    
class PhotoChangeLV(LoginRequiredMixin,ListView):
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
