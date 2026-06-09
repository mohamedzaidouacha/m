# -*- coding: utf-8 -*-
# Migration manuelle — ajout filière/année/âge étudiant + conditions clubs/events

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [

        # ── Utilisateur : filière, année, âge ────────────────────────────
        migrations.AddField(
            model_name='utilisateur',
            name='filiere',
            field=models.CharField(
                blank=True, null=True, max_length=20,
                choices=[
                    ('GENIE_IND', 'Génie Industriel'),
                    ('FINANCE',   'Finance'),
                    ('RESEAUX',   'Réseaux Informatiques'),
                    ('PREPA',     'Classe Préparatoire'),
                ],
                verbose_name='Filière',
            ),
        ),
        migrations.AddField(
            model_name='utilisateur',
            name='annee',
            field=models.CharField(
                blank=True, null=True, max_length=1,
                choices=[
                    ('1', '1ère année'),
                    ('2', '2ème année'),
                    ('3', '3ème année'),
                    ('4', '4ème année'),
                    ('5', '5ème année'),
                ],
                verbose_name="Année d'études",
            ),
        ),
        migrations.AddField(
            model_name='utilisateur',
            name='age',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Âge'),
        ),

        # ── Club : conditions d'adhésion ──────────────────────────────────
        migrations.AddField(
            model_name='club',
            name='cond_filiere',
            field=models.CharField(
                blank=True, null=True, max_length=20,
                choices=[
                    ('GENIE_IND', 'Génie Industriel'),
                    ('FINANCE',   'Finance'),
                    ('RESEAUX',   'Réseaux Informatiques'),
                    ('PREPA',     'Classe Préparatoire'),
                ],
                verbose_name='Filière requise (laisser vide = toutes)',
            ),
        ),
        migrations.AddField(
            model_name='club',
            name='cond_annee_min',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Année minimale requise'),
        ),
        migrations.AddField(
            model_name='club',
            name='cond_annee_max',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Année maximale requise'),
        ),
        migrations.AddField(
            model_name='club',
            name='cond_age_min',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Âge minimum requis'),
        ),
        migrations.AddField(
            model_name='club',
            name='cond_age_max',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Âge maximum requis'),
        ),

        # ── Evenement : vider les anciens événements (dates format texte incompatible)
        migrations.RunSQL(
            sql="DELETE FROM core_participation; DELETE FROM core_evenement;",
            reverse_sql=migrations.RunSQL.noop,
        ),

        # ── Evenement : changer date CharField → DateField ────────────────
        migrations.AlterField(
            model_name='evenement',
            name='date',
            field=models.DateField(verbose_name="Date de l'événement"),
        ),

        # ── Evenement : conditions de participation ───────────────────────
        migrations.AddField(
            model_name='evenement',
            name='cond_filiere',
            field=models.CharField(
                blank=True, null=True, max_length=20,
                choices=[
                    ('GENIE_IND', 'Génie Industriel'),
                    ('FINANCE',   'Finance'),
                    ('RESEAUX',   'Réseaux Informatiques'),
                    ('PREPA',     'Classe Préparatoire'),
                ],
                verbose_name='Filière requise (laisser vide = toutes)',
            ),
        ),
        migrations.AddField(
            model_name='evenement',
            name='cond_annee_min',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Année minimale requise'),
        ),
        migrations.AddField(
            model_name='evenement',
            name='cond_annee_max',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Année maximale requise'),
        ),
        migrations.AddField(
            model_name='evenement',
            name='cond_age_min',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Âge minimum requis'),
        ),
        migrations.AddField(
            model_name='evenement',
            name='cond_age_max',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Âge maximum requis'),
        ),
    ]
