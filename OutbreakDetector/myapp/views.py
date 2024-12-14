from .models import Escola, Curs, Informe
import json
from datetime import date
from django import forms
from django.urls import reverse
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Count
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

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

class AlertasView(TemplateView):
    template_name = 'alertas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        informes = Informe.objects.all()

        # Aggregate the count of each `Simptoma`
        result = (
            Informe.objects.filter(
                data=date.today(),          # Filter by current date
            )
            .values('curs__escola__nom', 'simptoma')             # Group by simptoma
            .annotate(simptoma_count=Count('id'))  # Count records in each group
            .filter(simptoma_count__gt=5)   # Only include groups with more than 5 records
        )
        alerts = []
        for row in result:
            key = row['simptoma']
            count = row['simptoma_count']
            severity = 'Baixa' if count <= 5 else 'Mitjana'
            severity = 'Alta' if count > 10 else severity
            alert = {
                'simptoma': {
                    'key': key,
                    'label': Informe.Simptoma(key).label,
                },
                'quantitat': count,
                'escola': row['curs__escola__nom'],
                'gravetat': severity,
            }
            alerts.append(alert)
        context['alerts'] = alerts
        return context
    
class AlertasEscolaView(TemplateView):
    template_name = 'alertas_escola.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if 'escola' parameter is in the URL
        escola_id = kwargs.get('escola')
        if escola_id:
            # Get the Escola object
            try:
                escola = Escola.objects.get(pk=escola_id)
                context['escola'] = escola
            except Escola.DoesNotExist:
                context['error'] = "Escola not found"
                return context

            # Filter `Informe` records by `Curs` linked to the specified `Escola`
            informes = Informe.objects.filter(curs__escola=escola)

            # Aggregate the count of each `Simptoma`
            result = (
                Informe.objects.filter(
                    curs__escola_id=escola_id,  # Filter by Escola ID
                    data=date.today(),          # Filter by current date
                )
                .values('simptoma')             # Group by simptoma
                .annotate(simptoma_count=Count('id'))  # Count records in each group
                .filter(simptoma_count__gt=5)   # Only include groups with more than 5 records
            )
            alerts = []
            for row in result:
                key = row['simptoma']
                count = row['simptoma_count']
                severity = 'Baixa' if count <= 5 else 'Mitjana'
                severity = 'Alta' if count > 10 else severity
                alert = {
                    'simptoma': {
                        'key': key,
                        'label': Informe.Simptoma(key).label,
                    },
                    'quantitat': count,
                    'escola': escola.nom,
                    'gravetat': severity,
                }
                alerts.append(alert)
            context['alerts'] = alerts
        else:
            context['alerts'] = []
            context['error'] = "No escola parameter provided"
        
        return context