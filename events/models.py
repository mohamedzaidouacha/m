# -*- coding: utf-8 -*-
# pyrefly: ignore [missing-import]
from django.db import models
from accounts.models import Utilisateur, FILIERE_CHOICES
from clubs.models import Club

class Evenement(models.Model):
    titre       = models.CharField(max_length=150)
    date        = models.DateField(verbose_name="Date de l'événement")
    lieu        = models.CharField(max_length=200)
    description = models.TextField()
    image       = models.FileField(upload_to='events/covers/', blank=True, null=True)
    club        = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='evenements')

    # ── Conditions de participation ───────────────────────────────────────
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
            return False, f"Cet événement est réservé aux étudiants de {filiere_nom}."
        annee_int = int(etudiant.annee) if etudiant.annee else None
        if self.cond_annee_min and (not annee_int or annee_int < self.cond_annee_min):
            return False, f"Il faut être au moins en {self.cond_annee_min}ème année."
        if self.cond_annee_max and (not annee_int or annee_int > self.cond_annee_max):
            return False, f"Cet événement est réservé aux années ≤ {self.cond_annee_max}."
        if self.cond_age_min and (not etudiant.age or etudiant.age < self.cond_age_min):
            return False, f"Âge minimum requis : {self.cond_age_min} ans."
        if self.cond_age_max and (not etudiant.age or etudiant.age > self.cond_age_max):
            return False, f"Âge maximum autorisé : {self.cond_age_max} ans."
        return True, ''

    def __str__(self):
        return self.titre

class Participation(models.Model):
    etudiant         = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='participations')
    evenement        = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='participants')
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.etudiant.username} participe à {self.evenement.titre}"


class EvenementImage(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='galerie')
    image = models.FileField(upload_to='events/gallery/')
    legende = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Image pour {self.evenement.titre}"
