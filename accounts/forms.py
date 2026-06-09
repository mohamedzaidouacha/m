# pyrefly: ignore [missing-import]
from django import forms
# pyrefly: ignore [missing-import]
from django.contrib.auth.forms import AuthenticationForm
# pyrefly: ignore [missing-import]
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur

class CustomUserCreationForm(UserCreationForm):
    ALLOWED_ROLE_CHOICES = (
        ('RESPONSABLE', 'Responsable de club'),
        ('ETUDIANT', 'Étudiant'),
    )

    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ('username', 'email', 'role', 'filiere', 'annee', 'age')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = self.ALLOWED_ROLE_CHOICES
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_role(self):
        role = self.cleaned_data.get('role')
        allowed_roles = {choice[0] for choice in self.ALLOWED_ROLE_CHOICES}
        if role not in allowed_roles:
            raise forms.ValidationError("Had role ma3andkch l7e9 t5tarou f l'inscription.")
        return role


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                "Had lcompte mabannih ladmin w ma9aderch ydkhol daba.",
                code='inactive',
            )
