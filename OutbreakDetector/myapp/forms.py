from django import forms
from .models import Escola

class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = ['nom', 'regio', 'municipi']
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': "Escriu el nom de l'escola", 'class': 'form-control'}),
            'regio': forms.TextInput(attrs={'placeholder': "Escriu la regió", 'class': 'form-control'}),
            'municipi': forms.TextInput(attrs={'placeholder': "Escriu el municipi", 'class': 'form-control'}),
        }
