from django import forms
from .models import Evenement


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(item, initial) for item in data]
        if not data:
            return []
        return [single_file_clean(data, initial)]

class EvenementForm(forms.ModelForm):
    galerie = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={'class': 'form-control'}),
        help_text="Vous pouvez sélectionner plusieurs images."
    )

    class Meta:
        model = Evenement
        fields = ['titre', 'date', 'lieu', 'description', 'image', 'cond_filiere', 'cond_annee_min', 'cond_annee_max', 'cond_age_min', 'cond_age_max']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
