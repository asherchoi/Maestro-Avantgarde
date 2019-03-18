from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView,DetailView
from photo.models import Photo
#create your views here

#--templateView
class MakeartView(TemplateView):
    template_name = 'photo/photo_Mylist.html'


#--templateView
class HomeView(ListView):
    template_name = 'home.html'
    model = Photo
    paginate_by = 4

#--- User Creation
class UserCreateView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register_done')

class UserCreateDoneTV(TemplateView):
    template_name = 'registration/register_done.html'

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin,cls).as_view(**initkwargs)
        return login_required(view)


