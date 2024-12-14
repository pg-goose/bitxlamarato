from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import Escola, Curs
from django import forms

class RedirectUserView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return '/admin/'
        else:
            return '/alertas/'

# Form Definitions
class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = ['nom', 'regio', 'municipi']

class CursForm(forms.ModelForm):
    class Meta:
        model = Curs
        fields = ['nom', 'numAlumnes', 'edatMitja', 'escola']

# View for "Escoles" page
class EscolesAdminView(UserPassesTestMixin, TemplateView):
    template_name = 'escoles.html'

    def test_func(self):
        """Ensure only superusers can access this view."""
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """Handle unauthorized access."""
        if self.request.user.is_authenticated:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return redirect(reverse('login'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['escola_form'] = EscolaForm()
        context['curs_form'] = CursForm()
        return context

    def post(self, request, *args, **kwargs):
        if 'escola_form_submit' in request.POST:  # Handle Escola form submission
            escola_form = EscolaForm(request.POST)
            if escola_form.is_valid():
                escola_form.save()
                return redirect(reverse('escoles'))  # Redirect to refresh the page
        elif 'curs_form_submit' in request.POST:  # Handle Curs form submission
            curs_form = CursForm(request.POST)
            if curs_form.is_valid():
                curs_form.save()
                return redirect(reverse('escoles'))  # Redirect to refresh the page

        # If form submissions fail, reload with errors
        context = self.get_context_data()
        context['escola_form'] = escola_form
        context['curs_form'] = curs_form
        return render(request, self.template_name, context)
