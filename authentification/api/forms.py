# forms.py
from django import forms
from .models import Agent, User

class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['nom', 'prenom', 'adresse', 'email', 'date_naissance', 'sexe', 'telephone', 'matricule', 'chef']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }