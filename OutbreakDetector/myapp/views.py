from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin


class RedirectUserView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return '/admin/'
        else:
            return '/alertas/'

class AdminOutbreaksView(UserPassesTestMixin, TemplateView):
    template_name = 'admin_outbreaks.html'

    def test_func(self):
        return self.request.user.is_superuser


from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .models import Escola
from .forms import EscolaForm  # Create a form class for the model

class EscolaAddView(FormView):
    template_name = 'nova_escola.html'  # Template for the form
    form_class = EscolaForm            # Use the form class for Escola
    success_url = reverse_lazy('success_page')  # Redirect URL after form submission

    def form_valid(self, form):
        # Save the form data as a new Escola object
        form.save()
        return super().form_valid(form)
