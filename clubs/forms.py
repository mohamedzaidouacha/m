# pyrefly: ignore [missing-import]
from django import forms
from .models import Club

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['nom', 'description', 'logo', 'cond_filiere', 'cond_annee_min', 'cond_annee_max', 'cond_age_min', 'cond_age_max']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
