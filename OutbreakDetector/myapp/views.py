import qrcode
import json
from datetime import date
from io import BytesIO

from django import forms
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .models import Curs, Escola, Informe

class RedirectUserView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            relative_url = reverse('escoles')  # Reverse lookup for your route
        else:
            relative_url = reverse('alertas')  # Reverse lookup for your route
        
        # Build absolute URI
        return self.request.build_absolute_uri(relative_url)

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


class EscolaByIdView(View):
    def get(self, request, *args, **kwargs):
        escola_id = self.kwargs.get('escola')
        escola = get_object_or_404(Escola, id=escola_id)
        cursos = Curs.objects.filter(escola=escola).values('id', 'nom') 
        return JsonResponse({
            'id': escola.id,
            'nom': escola.nom,
            'regio': escola.regio,
            'municipi': escola.municipi,
            'lat': escola.lat,
            'lon': escola.lon,
            'cursos': list(cursos),
        })

class QRCodeDisplayView(TemplateView):
    template_name = 'reportQR.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['escoles'] = list(Escola.objects.all())
        context['base_url'] = self.request.build_absolute_uri('/').rstrip('/')  # Remove trailing slash
        return context

class QRCodeView(View):
    def get(self, request, *args, **kwargs):
        # Retrieve the 'url' parameter from the query string (e.g., ?url=some-url)
        url = request.GET.get('url', '/')
        
        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Create an image of the QR code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image to a BytesIO stream
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Return the image as an HTTP response
        return HttpResponse(buffer, content_type="image/png")
    
    
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

        escoles = Escola.objects.all()
        context['escoles'] = escoles

        # Aggregate the count of each `Simptoma`
        result = (
            Informe.objects.filter(
                data=date.today(),          # Filter by current date
            )
            .values('curs__escola__nom', 'simptoma', "curs__escola__lat", "curs__escola__lon")             # Group by simptoma
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
                'lat': row['curs__escola__lat'],
                'lon': row['curs__escola__lon'],
            }
            alerts.append(alert)
        context['alertas'] = alerts
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
                context['escola'] = {
                    'id': escola.id,
                    'nom': escola.nom,
                    'regio': escola.regio,
                    'municipi': escola.municipi,
                    'lat': escola.lat,
                    'lon': escola.lon
                }
            except Escola.DoesNotExist:
                context['error'] = "Escola not found"
                return context

            # Filter `Informe` records by `Curs` linked to the specified `Escola`
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
            context['alertas'] = alerts
        else:
            context['alertas'] = []
            context['error'] = "No escola parameter provided"
        
        return context
    
class RoadmapView(TemplateView):
    template_name = 'roadmap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context