# -*- coding: utf-8 -*-
# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.contrib.auth.models import AbstractUser

# ─────────────────────────────────────────────
#  Choix globaux
# ─────────────────────────────────────────────
FILIERE_CHOICES = (
    ('GENIE_IND',  'Génie Industriel'),
    ('FINANCE',    'Finance'),
    ('RESEAUX',    'Réseaux Informatiques'),
    ('PREPA',      'Classe Préparatoire'),
)

ANNEE_CHOICES = (
    ('1', '1ère année'),
    ('2', '2ème année'),
    ('3', '3ème année'),
    ('4', '4ème année'),
    ('5', '5ème année'),
)

class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN',       'Administrateur'),
        ('RESPONSABLE', 'Responsable de club'),
        ('ETUDIANT',    'Étudiant'),
    )
    role    = models.CharField(max_length=15, choices=ROLE_CHOICES, default='ETUDIANT')

    # ── Champs spécifiques aux étudiants ──────────────────────────────────
    filiere = models.CharField(
        max_length=20, choices=FILIERE_CHOICES,
        blank=True, null=True,
        verbose_name="Filière"  
    )
    annee   = models.CharField(
        max_length=1, choices=ANNEE_CHOICES,
        blank=True, null=True,
        verbose_name="Année d'études"
    )
    age     = models.PositiveSmallIntegerField(
        blank=True, null=True,
        verbose_name="Âge"
    )

    def save(self, *args, **kwargs):
        # Any internal ADMIN account must be able to access Django admin.
        if self.role == 'ADMIN':
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

    def get_filiere_display_fr(self):
        return dict(FILIERE_CHOICES).get(self.filiere, self.filiere or '-')

    def get_annee_display_fr(self):
        return dict(ANNEE_CHOICES).get(self.annee, self.annee or '-')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
