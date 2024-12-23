"""
URL configuration for OutbreakDetector project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from myapp.views import EscolesAdminView, InformeView, AlertasView, AlertasEscolaView, RedirectUserView, QRCodeView, QRCodeDisplayView, EscolaByIdView, RoadmapView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', RedirectUserView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('escoles/', EscolesAdminView.as_view(), name='escoles'),
    path('escoles/<int:escola>', EscolaByIdView.as_view(), name='escoles'),
    path('qr/', QRCodeView.as_view(), name='qr_code'),
    path('display-qr/', QRCodeDisplayView.as_view(), name='display_qr'),
    path('informe/<int:escola>/<int:curs>/', InformeView.as_view(), name='informe'),
    path('alertas/', AlertasView.as_view(), name='alertas'),
    path('alertas/<int:escola>', AlertasEscolaView.as_view(), name='alertas_escola'),
    path('roadmap/', RoadmapView.as_view(), name='roadmap'),
]
