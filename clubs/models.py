# -*- coding: utf-8 -*-
# pyrefly: ignore [missing-import]
from django.db import models
from accounts.models import Utilisateur, FILIERE_CHOICES

class Club(models.Model):
    nom          = models.CharField(max_length=100, unique=True)
    description  = models.TextField()
    logo         = models.FileField(upload_to='clubs/logos/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_valide   = models.BooleanField(default=False)
    responsable  = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name='clubs_geres'
    )

    # ── Conditions d'adhésion ─────────────────────────────────────────────
    cond_filiere  = models.CharField(
        max_length=20, choices=FILIERE_CHOICES,
        blank=True, null=True,
        verbose_name="Filière requise (laisser vide = toutes)"
    )
    cond_annee_min = models.PositiveSmallIntegerField(
        blank=True, null=True,
        verbose_name="Année minimale requise"
    )
    cond_annee_max = models.PositiveSmallIntegerField(
        blank=True, null=True,
        verbose_name="Année maximale requise"
    )
    cond_age_min  = models.PositiveSmallIntegerField(
        blank=True, null=True,
        verbose_name="Âge minimum requis"
    )
    cond_age_max  = models.PositiveSmallIntegerField(
        blank=True, null=True,
        verbose_name="Âge maximum requis"
    )

    def verifier_etudiant(self, etudiant):
        """Retourne (True, '') ou (False, 'message d\'erreur')."""
        if self.cond_filiere and etudiant.filiere != self.cond_filiere:
            filiere_nom = dict(FILIERE_CHOICES).get(self.cond_filiere, self.cond_filiere)
            return False, f"Ce club est réservé aux étudiants de {filiere_nom}."
        annee_int = int(etudiant.annee) if etudiant.annee else None
        if self.cond_annee_min and (not annee_int or annee_int < self.cond_annee_min):
            return False, f"Il faut être au moins en {self.cond_annee_min}ème année."
        if self.cond_annee_max and (not annee_int or annee_int > self.cond_annee_max):
            return False, f"Ce club est réservé aux années ≤ {self.cond_annee_max}."
        if self.cond_age_min and (not etudiant.age or etudiant.age < self.cond_age_min):
            return False, f"Âge minimum requis : {self.cond_age_min} ans."
        if self.cond_age_max and (not etudiant.age or etudiant.age > self.cond_age_max):
            return False, f"Âge maximum autorisé : {self.cond_age_max} ans."
        return True, ''

    def __str__(self):
        return self.nom

class Adhesion(models.Model):
    STATUT_CHOICES = (
        ('ATTENTE',  'En attente'),
        ('ACCEPTEE', 'Acceptée'),
        ('REFUSEE',  'Refusée'),
    )
    etudiant     = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='adhesions')
    club         = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='demandes_adhesion')
    statut       = models.CharField(max_length=10, choices=STATUT_CHOICES, default='ATTENTE')
    date_demande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.etudiant.username} → {self.club.nom} ({self.get_statut_display()})"
