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

from django.views.generic import TemplateView
from .models import Informe

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Informe, Escola, Curs
import json
from datetime import date

@method_decorator(csrf_exempt, name='dispatch')  # To allow POST requests without CSRF token
class InformeView(TemplateView):
    template_name = 'informe.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = kwargs.get('escola')
        curs = kwargs.get('curs')

        # Fetch escola and curs objects
        context['escola'] = escola
        context['curs'] = curs
        context['simptomes'] = [{'key': choice[0], 'label': choice[1]} for choice in Informe.Simptoma.choices]
        return context

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            escola_id = kwargs.get('escola')
            curs_id = kwargs.get('curs')

            escola = get_object_or_404(Escola, id=escola_id)
            curs = get_object_or_404(Curs, id=curs_id, escola=escola)
            simptomes = data.get('simptomes')
            print(simptomes)
            print(type(simptomes))

            for simptoma in simptomes:
                Informe.objects.create(
                    data=date.today(),
                    curs=curs,
                    simptoma=simptoma,
                )
            return JsonResponse({'status': 'success', 'message': 'Informe enviat correctament!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

