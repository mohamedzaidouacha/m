# -*- coding: utf-8 -*-
"""
Gestion des Clubs Étudiants — Interface Terminal
"""
import sys, io, os, shutil
from datetime import datetime

# Fix encoding Windows
if sys.platform == 'win32':
    os.system("")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8', errors='replace')

# pyrefly: ignore [missing-import]
from django.core.management.base import BaseCommand
# pyrefly: ignore [missing-import]
from django.contrib.auth import authenticate
from accounts.models import Utilisateur, FILIERE_CHOICES, ANNEE_CHOICES
from clubs.models import Club, Adhesion
from events.models import Evenement, Participation

# ─────────────────────────────────────────────
#  Couleurs ANSI
# ─────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"

# ─────────────────────────────────────────────
#  Centrage dynamique
# ─────────────────────────────────────────────
BOX_W = 60  # largeur de la boîte de contenu

def get_margin():
    """Retourne les espaces nécessaires pour centrer la boîte dans le terminal."""
    cols = shutil.get_terminal_size(fallback=(120, 30)).columns
    return " " * max(0, (cols - BOX_W) // 2)

# ─────────────────────────────────────────────
#  Helpers d'affichage (centrés)
# ─────────────────────────────────────────────
def clear():
    os.system("cls" if sys.platform == "win32" else "clear")

def p(texte=""):
    """Affiche une ligne vide (non centrée)."""
    print()

def pc(texte=""):
    """Affiche du texte centré dans le terminal."""
    try:    print(f"{get_margin()}{texte}")
    except: print(f"{get_margin()}{texte}".encode('ascii', errors='replace').decode('ascii'))

def saisir(invite):
    """Saisie centrée."""
    try:    return input(f"{get_margin()}  {C.CYAN}{C.BOLD}> {C.RESET}{C.WHITE}{invite}{C.RESET}").strip()
    except: return ""

def titre(texte, couleur=C.CYAN):
    pc()
    pc(f"{couleur}{C.BOLD}{'═' * BOX_W}{C.RESET}")
    inner = texte.center(BOX_W - 2)
    pc(f"{couleur}{C.BOLD}║{inner}║{C.RESET}")
    pc(f"{couleur}{C.BOLD}{'═' * BOX_W}{C.RESET}")

def sous_titre(texte, couleur=C.YELLOW):
    pc()
    pc(f"{couleur}{C.BOLD}  ── {texte} ──{C.RESET}")
    pc()

def option(num, texte, couleur=C.WHITE):
    pc(f"  {C.CYAN}{C.BOLD}[{num}]{C.RESET}  {couleur}{texte}{C.RESET}")

def succes(texte):
    pc(f"  {C.GREEN}{C.BOLD}[OK]{C.RESET}  {C.GREEN}{texte}{C.RESET}")

def erreur(texte):
    pc(f"  {C.RED}{C.BOLD}[!]{C.RESET}  {C.RED}{texte}{C.RESET}")

def info(texte):
    pc(f"  {C.YELLOW}{C.BOLD}[i]{C.RESET}  {C.YELLOW}{texte}{C.RESET}")

def separateur():
    pc(f"{C.DIM}{'─' * BOX_W}{C.RESET}")

def pause():
    saisir("Appuyez sur ENTREE pour continuer...")


# ─────────────────────────────────────────────
#  Helpers métier
# ─────────────────────────────────────────────
DICT_FILIERE = dict(FILIERE_CHOICES)
DICT_ANNEE   = dict(ANNEE_CHOICES)

def afficher_menu_filiere():
    """Affiche les filières numérotées et retourne la clé choisie ou None."""
    sous_titre("Choisir une filière", C.CYAN)
    filieres = list(FILIERE_CHOICES)
    for i, (_, label) in enumerate(filieres, 1):
        option(str(i), label)
    p()
    ch = saisir("Votre choix (1-4) : ")
    try:
        idx = int(ch) - 1
        if 0 <= idx < len(filieres):
            return filieres[idx][0]
    except ValueError:
        pass
    erreur("Choix invalide.")
    return None

def afficher_menu_annee(filiere_code):
    """Affiche les années disponibles selon la filière et retourne la valeur choisie (str)."""
    sous_titre("Choisir une année", C.CYAN)
    is_prepa = (filiere_code == 'PREPA')
    annees = [('1', '1ère année'), ('2', '2ème année')] if is_prepa else list(ANNEE_CHOICES)
    for i, (_, label) in enumerate(annees, 1):
        option(str(i), label)
    p()
    ch = saisir(f"Votre choix (1-{len(annees)}) : ")
    try:
        idx = int(ch) - 1
        if 0 <= idx < len(annees):
            return annees[idx][0]
    except ValueError:
        pass
    erreur("Choix invalide.")
    return None

def saisir_age():
    """Saisit et valide l'âge de l'étudiant. Retourne int ou None."""
    for _ in range(3):
        raw = saisir("Votre âge : ")
        try:
            age = int(raw)
            if 14 <= age <= 60:
                return age
            else:
                erreur("Âge doit être entre 14 et 60.")
        except ValueError:
            erreur("Veuillez entrer un nombre entier.")
    return None

def saisir_date(invite="Date (JJ/MM/AAAA) : "):
    """Saisit et valide une date. Retourne un objet date ou None."""
    for _ in range(3):
        raw = saisir(invite)
        try:
            d = datetime.strptime(raw, "%d/%m/%Y").date()
            return d
        except ValueError:
            erreur(f"Format invalide : '{raw}'. Utilisez JJ/MM/AAAA (ex: 15/06/2025).")
    erreur("Trop de tentatives. Date non enregistrée.")
    return None

def saisir_entier_optionnel(invite, min_val=1, max_val=5):
    """Saisit un entier optionnel (ENTREE = None)."""
    raw = saisir(invite)
    if not raw:
        return None
    try:
        val = int(raw)
        if min_val <= val <= max_val:
            return val
        erreur(f"Valeur doit être entre {min_val} et {max_val}.")
    except ValueError:
        erreur("Valeur invalide - ignorée.")
    return None

def afficher_conditions_club(club):
    """Affiche un résumé des conditions d'un club."""
    conditions = []
    if club.cond_filiere:
        conditions.append(f"Filière : {DICT_FILIERE.get(club.cond_filiere, club.cond_filiere)}")
    if club.cond_annee_min:
        conditions.append(f"Année ≥ {club.cond_annee_min}")
    if club.cond_annee_max:
        conditions.append(f"Année ≤ {club.cond_annee_max}")
    if club.cond_age_min:
        conditions.append(f"Âge ≥ {club.cond_age_min}")
    if club.cond_age_max:
        conditions.append(f"Âge ≤ {club.cond_age_max}")
    if conditions:
        pc(f"   {C.MAGENTA}Conditions : {' | '.join(conditions)}{C.RESET}")
    else:
        pc(f"   {C.DIM}Ouvert à tous{C.RESET}")

def afficher_conditions_event(evt):
    """Affiche un résumé des conditions d'un événement."""
    conditions = []
    if evt.cond_filiere:
        conditions.append(f"Filière : {DICT_FILIERE.get(evt.cond_filiere, evt.cond_filiere)}")
    if evt.cond_annee_min:
        conditions.append(f"Année ≥ {evt.cond_annee_min}")
    if evt.cond_annee_max:
        conditions.append(f"Année ≤ {evt.cond_annee_max}")
    if evt.cond_age_min:
        conditions.append(f"Âge ≥ {evt.cond_age_min}")
    if evt.cond_age_max:
        conditions.append(f"Âge ≤ {evt.cond_age_max}")
    if conditions:
        pc(f"   {C.MAGENTA}Conditions : {' | '.join(conditions)}{C.RESET}")
    else:
        pc(f"   {C.DIM}Ouvert à tous{C.RESET}")


# ─────────────────────────────────────────────
#  Commande Django
# ─────────────────────────────────────────────
class Command(BaseCommand):
    help = "Lance l'application de gestion de clubs étudiants"

    def handle(self, *args, **kwargs):
        self.creer_admin_par_defaut()
        while True:
            clear()
            titre("GESTION DES CLUBS ETUDIANTS", C.CYAN)
            p()
            option("1", "Se connecter")
            option("2", "Créer un compte")
            option("3", "Quitter")
            p()
            separateur()
            choix = saisir("Votre choix : ")
            if choix == "1":   self.connexion()
            elif choix == "2": self.inscription()
            elif choix == "3": succes("Au revoir !"); sys.exit(0)
            else: erreur("Option invalide."); pause()

    # ──────────────────────────────────────────
    def creer_admin_par_defaut(self):
        if not Utilisateur.objects.filter(role="ADMIN").exists() and \
           not Utilisateur.objects.filter(is_superuser=True).exists():
            Utilisateur.objects.create_user(
                username="admin", password="admin123",
                first_name="Admin", last_name="Systeme",
                role="ADMIN", is_staff=True, is_superuser=True,
            )
            p()
            succes("Compte administrateur créé automatiquement !")
            pc(f"  {C.YELLOW}{C.BOLD}Utilisateur : admin{C.RESET}")
            pc(f"  {C.YELLOW}{C.BOLD}Mot de passe : admin123{C.RESET}")
            p()
            info("Connectez-vous en tant qu'admin pour valider les clubs.")
            pause()

    # ──────────────────────────────────────────
    def inscription(self):
        clear()
        titre("CREATION DE COMPTE", C.GREEN)
        p()

        username = saisir("Nom d'utilisateur : ")
        if not username:
            erreur("Nom d'utilisateur vide."); pause(); return
        if Utilisateur.objects.filter(username=username).exists():
            erreur("Ce nom d'utilisateur est déjà pris."); pause(); return

        password = saisir("Mot de passe      : ")
        nom      = saisir("Nom               : ")
        prenom   = saisir("Prénom            : ")

        p()
        sous_titre("Choisir un rôle")
        option("1", "Étudiant")
        option("2", "Responsable de club")
        p()
        role_choix = saisir("Votre rôle (1 ou 2) : ")
        role = "RESPONSABLE" if role_choix == "2" else "ETUDIANT"

        filiere = None
        annee   = None
        age     = None

        if role == "ETUDIANT":
            clear()
            titre("PROFIL ETUDIANT", C.GREEN)

            # ── Filière ─────────────────────────────────────────────────
            filiere = afficher_menu_filiere()
            if not filiere:
                erreur("Filière invalide. Inscription annulée."); pause(); return

            # ── Année d'études ──────────────────────────────────────────
            annee = afficher_menu_annee(filiere)
            if not annee:
                erreur("Année invalide. Inscription annulée."); pause(); return

            # ── Âge ─────────────────────────────────────────────────────
            p()
            age = saisir_age()
            if age is None:
                erreur("Âge invalide. Inscription annulée."); pause(); return

        Utilisateur.objects.create_user(
            username=username, password=password,
            last_name=nom, first_name=prenom,
            role=role,
            filiere=filiere, annee=annee, age=age,
        )
        p()
        succes(f"Compte créé avec succès ! Rôle : {role}")
        if role == "ETUDIANT":
            info(f"Filière : {DICT_FILIERE.get(filiere, filiere)}")
            info(f"Année   : {DICT_ANNEE.get(annee, annee)}")
            info(f"Âge     : {age} ans")
        pause()

    # ──────────────────────────────────────────
    def connexion(self):
        clear()
        titre("CONNEXION", C.BLUE)
        p()
        username = saisir("Nom d'utilisateur : ")
        password = saisir("Mot de passe      : ")
        user = authenticate(username=username, password=password)
        if user is None:
            erreur("Identifiants incorrects."); pause(); return
        p()
        succes(f"Bienvenue {user.first_name} {user.last_name} ({user.role})")
        pause()
        self.menu_principal(user)

    def menu_principal(self, user):
        while True:
            if user.is_superuser or user.role == "ADMIN":
                continuer = self.menu_admin(user)
            elif user.role == "RESPONSABLE":
                continuer = self.menu_responsable(user)
            else:
                continuer = self.menu_etudiant(user)
            if not continuer:
                info("Déconnexion effectuée.")
                pause()
                break

    # ══════════════════════════════════════════
    #  MENU ADMIN
    # ══════════════════════════════════════════
    def menu_admin(self, user):
        clear()
        titre("ADMINISTRATEUR", C.RED)
        p()
        option("1", "Clubs en attente de validation")
        option("2", "Valider un club")
        option("3", "Liste des utilisateurs")
        option("4", "Se déconnecter")
        p()
        separateur()
        choix = saisir("Votre choix : ")

        if choix == "1":
            clear()
            sous_titre("Clubs en attente", C.YELLOW)
            clubs = list(Club.objects.filter(est_valide=False))
            if not clubs:
                info("Aucun club en attente.")
            else:
                for c in clubs:
                    pc(f"  {C.BOLD}{C.WHITE}ID {c.id}{C.RESET} {C.DIM}|{C.RESET} "
                       f"{C.CYAN}{c.nom}{C.RESET} {C.DIM}|{C.RESET} "
                       f"{C.YELLOW}Resp: {c.responsable.username}{C.RESET}")
            pause()

        elif choix == "2":
            cid = saisir("ID du club à valider : ")
            try:
                club = Club.objects.get(id=int(cid))
                club.est_valide = True
                club.save()
                succes(f"Club '{club.nom}' validé !")
            except (Club.DoesNotExist, ValueError):
                erreur("Club introuvable.")
            pause()

        elif choix == "3":
            clear()
            sous_titre("Tous les utilisateurs", C.CYAN)
            for u in Utilisateur.objects.all():
                rc = C.RED if u.role == "ADMIN" else (C.MAGENTA if u.role == "RESPONSABLE" else C.GREEN)
                profil = ""
                if u.role == "ETUDIANT":
                    profil = (f" {C.DIM}|{C.RESET} "
                              f"{C.BLUE}{DICT_FILIERE.get(u.filiere, '-')}{C.RESET} "
                              f"{C.DIM}An:{u.annee or '-'} Âge:{u.age or '-'}{C.RESET}")
                pc(f"  {C.WHITE}{u.username}{C.RESET} {C.DIM}|{C.RESET} "
                   f"{u.last_name} {u.first_name} {C.DIM}|{C.RESET} "
                   f"{rc}{C.BOLD}{u.role}{C.RESET}{profil}")
            pause()

        elif choix == "4":
            return False
        else:
            erreur("Option invalide."); pause()
        return True

    # ══════════════════════════════════════════
    #  MENU RESPONSABLE
    # ══════════════════════════════════════════
    def menu_responsable(self, user):
        clear()
        titre("RESPONSABLE DE CLUB", C.MAGENTA)
        p()

        try:
            mon_club = Club.objects.get(responsable=user)
            statut = (f"{C.GREEN}Validé{C.RESET}" if mon_club.est_valide
                      else f"{C.YELLOW}En attente{C.RESET}")
            nb_m = Adhesion.objects.filter(club=mon_club, statut="ACCEPTEE").count()
            nb_a = Adhesion.objects.filter(club=mon_club, statut="ATTENTE").count()
            pc(f"  {C.CYAN}{C.BOLD}{mon_club.nom}{C.RESET} — {statut}")
            pc(f"  {C.GREEN}{nb_m} membre(s){C.RESET} {C.DIM}|{C.RESET} {C.YELLOW}{nb_a} demande(s) en attente{C.RESET}")
            p()
        except Club.DoesNotExist:
            mon_club = None
            info("Vous n'avez pas encore de club.")
            p()

        option("1", "Créer mon club")
        option("2", "Définir/Modifier les conditions d'adhésion")
        option("3", "Gérer les demandes d'adhésion")
        option("4", "Voir les membres du club")
        option("5", "Gérer les événements")
        option("6", "Se déconnecter")
        p()
        separateur()
        choix = saisir("Votre choix : ")

        if choix == "1":
            if Club.objects.filter(responsable=user).exists():
                erreur("Vous avez déjà un club.")
            else:
                nom  = saisir("Nom du club    : ")
                desc = saisir("Description    : ")
                Club.objects.create(nom=nom, description=desc, responsable=user)
                succes("Club créé ! En attente de validation par l'administrateur.")
            pause()

        elif choix == "2":
            if not mon_club:
                erreur("Vous n'avez pas encore de club."); pause(); return True
            self._definir_conditions_club(mon_club)

        elif choix == "3":
            self._gerer_demandes(mon_club)

        elif choix == "4":
            self._voir_membres(mon_club)

        elif choix == "5":
            self._gerer_evenements(mon_club)

        elif choix == "6":
            return False
        else:
            erreur("Option invalide."); pause()
        return True

    # ──────────────────────────────────────────
    def _definir_conditions_club(self, club):
        """Permet au responsable de définir les conditions d'adhésion."""
        clear()
        titre(f"CONDITIONS - {club.nom}", C.MAGENTA)
        p()
        info("Laissez vide (ENTREE) pour 'aucune restriction'.")
        p()

        # Filière
        pc(f"  {C.CYAN}{C.BOLD}Filière requise:{C.RESET}")
        option("0", "Toutes les filières (aucune restriction)")
        for i, (_, label) in enumerate(FILIERE_CHOICES, 1):
            option(str(i), label)
        p()
        ch = saisir("Choix (0-4) : ")
        try:
            idx = int(ch)
            if idx == 0:
                club.cond_filiere = None
            elif 1 <= idx <= len(FILIERE_CHOICES):
                club.cond_filiere = FILIERE_CHOICES[idx - 1][0]
            else:
                erreur("Choix invalide - ignoré.")
        except ValueError:
            pass  # garde la valeur actuelle

        # Années
        p()
        pc(f"  {C.CYAN}{C.BOLD}Restriction d'année :{C.RESET}")
        club.cond_annee_min = saisir_entier_optionnel("Année minimale (1-5, ENTREE=aucune) : ", 1, 5)
        club.cond_annee_max = saisir_entier_optionnel("Année maximale (1-5, ENTREE=aucune) : ", 1, 5)

        # Âge
        p()
        pc(f"  {C.CYAN}{C.BOLD}Restriction d'âge :{C.RESET}")
        club.cond_age_min = saisir_entier_optionnel("Âge minimum (ENTREE=aucun) : ", 14, 60)
        club.cond_age_max = saisir_entier_optionnel("Âge maximum (ENTREE=aucun) : ", 14, 60)

        club.save()
        succes("Conditions mises à jour !")
        pause()

    # ──────────────────────────────────────────
    def _gerer_demandes(self, mon_club):
        if not mon_club or not mon_club.est_valide:
            erreur("Club non disponible ou non validé."); pause(); return
        clear()
        sous_titre(f"Demandes d'adhésion — {mon_club.nom}", C.MAGENTA)
        demandes = list(Adhesion.objects.filter(club=mon_club, statut="ATTENTE").select_related("etudiant"))
        if not demandes:
            info("Aucune demande en attente.")
        else:
            for d in demandes:
                etd = d.etudiant
                profil = (f"{DICT_FILIERE.get(etd.filiere, '?')} | "
                          f"An {etd.annee or '?'} | "
                          f"Âge {etd.age or '?'}")
                pc(f"  {C.WHITE}{C.BOLD}ID {d.id}{C.RESET} {C.DIM}|{C.RESET} "
                   f"{C.CYAN}{etd.username}{C.RESET} "
                   f"{C.DIM}({etd.last_name} {etd.first_name}){C.RESET}")
                pc(f"   {C.YELLOW}{profil}{C.RESET}")
            p()
            did = saisir("ID demande à traiter (ENTREE pour passer) : ")
            if did:
                try:
                    d = Adhesion.objects.get(id=int(did), club=mon_club)
                    p()
                    option("A", "Accepter", C.GREEN)
                    option("R", "Refuser",  C.RED)
                    rep = saisir("Votre décision : ")
                    if rep.upper() == "A":
                        d.statut = "ACCEPTEE"; d.save(); succes("Demande acceptée !")
                    elif rep.upper() == "R":
                        d.statut = "REFUSEE"; d.save(); succes("Demande refusée.")
                    else:
                        erreur("Réponse invalide.")
                except (Adhesion.DoesNotExist, ValueError):
                    erreur("ID invalide.")
        pause()

    # ──────────────────────────────────────────
    def _voir_membres(self, mon_club):
        if not mon_club:
            erreur("Vous n'avez pas encore de club."); pause(); return
        clear()
        sous_titre(f"Membres — {mon_club.nom}", C.MAGENTA)
        membres = list(Adhesion.objects.filter(club=mon_club, statut="ACCEPTEE").select_related("etudiant"))
        if not membres:
            info("Aucun membre pour le moment.")
        else:
            pc(f"  {C.WHITE}{C.BOLD}Total : {len(membres)} membre(s){C.RESET}")
            p()
            for i, m in enumerate(membres, 1):
                etd = m.etudiant
                profil = (f"{DICT_FILIERE.get(etd.filiere, '?')} | "
                          f"An {etd.annee or '?'} | "
                          f"Âge {etd.age or '?'}")
                pc(f"  {C.GREEN}{i}.{C.RESET} "
                   f"{C.WHITE}{C.BOLD}{etd.last_name} {etd.first_name}{C.RESET} "
                   f"{C.DIM}({etd.username}){C.RESET}")
                pc(f"   {C.YELLOW}{profil}{C.RESET}")
        pause()

    # ──────────────────────────────────────────
    def _gerer_evenements(self, mon_club):
        if not mon_club or not mon_club.est_valide:
            erreur("Club non disponible ou non validé."); pause(); return
        clear()
        titre(f"EVENEMENTS — {mon_club.nom}", C.MAGENTA)
        p()
        option("1", "Ajouter un événement")
        option("2", "Définir conditions d'un événement")
        option("3", "Voir participants d'un événement")
        p()
        opt = saisir("Choix : ")

        if opt == "1":
            p()
            t    = saisir("Titre       : ")
            date = saisir_date("Date de l'événement (JJ/MM/AAAA) : ")
            if date is None:
                erreur("Date invalide. Événement non créé."); pause(); return
            l    = saisir("Lieu        : ")
            desc = saisir("Description : ")

            evt = Evenement.objects.create(
                titre=t, date=date, lieu=l, description=desc, club=mon_club
            )
            succes(f"Événement '{t}' créé pour le {date.strftime('%d/%m/%Y')} !")

            # Proposer conditions immédiatement
            p()
            if saisir("Définir des conditions maintenant ? (o/n) : ").lower() == 'o':
                self._definir_conditions_event(evt)
            else:
                pause()

        elif opt == "2":
            evts = list(Evenement.objects.filter(club=mon_club))
            if not evts:
                info("Aucun événement."); pause(); return
            p()
            for e in evts:
                pc(f"  {C.WHITE}{C.BOLD}ID {e.id}{C.RESET} {C.DIM}|{C.RESET} "
                   f"{C.CYAN}{e.titre}{C.RESET} {C.DIM}| {e.date.strftime('%d/%m/%Y')}{C.RESET}")
            eid = saisir("ID de l'événement : ")
            try:
                evt = Evenement.objects.get(id=int(eid), club=mon_club)
                self._definir_conditions_event(evt)
            except (Evenement.DoesNotExist, ValueError):
                erreur("ID invalide."); pause()

        elif opt == "3":
            evts = list(Evenement.objects.filter(club=mon_club))
            if not evts:
                info("Aucun événement."); pause(); return
            p()
            for e in evts:
                pc(f"  {C.WHITE}{C.BOLD}ID {e.id}{C.RESET} {C.DIM}|{C.RESET} "
                   f"{C.CYAN}{e.titre}{C.RESET} {C.DIM}| {e.date.strftime('%d/%m/%Y')}{C.RESET}")
            eid = saisir("ID de l'événement : ")
            try:
                evt = Evenement.objects.get(id=int(eid), club=mon_club)
                parts = list(Participation.objects.filter(evenement=evt).select_related("etudiant"))
                p()
                sous_titre(f"Participants — {evt.titre}", C.CYAN)
                if not parts:
                    info("Aucun participant.")
                for pp in parts:
                    etd = pp.etudiant
                    pc(f"  {C.GREEN}*{C.RESET} "
                       f"{C.WHITE}{etd.last_name} {etd.first_name}{C.RESET} "
                       f"{C.DIM}({etd.username}){C.RESET}")
            except (Evenement.DoesNotExist, ValueError):
                erreur("ID invalide.")
            pause()
        else:
            erreur("Option invalide."); pause()

    # ──────────────────────────────────────────
    def _definir_conditions_event(self, evt):
        """Permet au responsable de définir les conditions de participation à un événement."""
        clear()
        titre(f"CONDITIONS - {evt.titre}", C.MAGENTA)
        p()
        info("Laissez vide (ENTREE) pour 'aucune restriction'.")
        p()

        # Filière
        pc(f"  {C.CYAN}{C.BOLD}Filière requise:{C.RESET}")
        option("0", "Toutes les filières (aucune restriction)")
        for i, (_, label) in enumerate(FILIERE_CHOICES, 1):
            option(str(i), label)
        p()
        ch = saisir("Choix (0-4) : ")
        try:
            idx = int(ch)
            if idx == 0:
                evt.cond_filiere = None
            elif 1 <= idx <= len(FILIERE_CHOICES):
                evt.cond_filiere = FILIERE_CHOICES[idx - 1][0]
            else:
                erreur("Choix invalide - ignoré.")
        except ValueError:
            pass

        # Années
        p()
        pc(f"  {C.CYAN}{C.BOLD}Restriction d'année :{C.RESET}")
        evt.cond_annee_min = saisir_entier_optionnel("Année minimale (1-5, ENTREE=aucune) : ", 1, 5)
        evt.cond_annee_max = saisir_entier_optionnel("Année maximale (1-5, ENTREE=aucune) : ", 1, 5)

        # Âge
        p()
        pc(f"  {C.CYAN}{C.BOLD}Restriction d'âge :{C.RESET}")
        evt.cond_age_min = saisir_entier_optionnel("Âge minimum (ENTREE=aucun) : ", 14, 60)
        evt.cond_age_max = saisir_entier_optionnel("Âge maximum (ENTREE=aucun) : ", 14, 60)

        evt.save()
        succes("Conditions de l'événement mises à jour !")
        pause()

    # ══════════════════════════════════════════
    #  MENU ETUDIANT
    # ══════════════════════════════════════════
    def menu_etudiant(self, user):
        clear()
        titre("ESPACE ETUDIANT", C.GREEN)
        p()

        # Profil affiché en haut
        profil_filiere = DICT_FILIERE.get(user.filiere, user.filiere or '?')
        profil_annee   = DICT_ANNEE.get(user.annee, user.annee or '?')
        pc(f"  {C.YELLOW}{C.BOLD}Mon profil :{C.RESET} "
           f"{C.CYAN}{profil_filiere}{C.RESET} — "
           f"{C.WHITE}{profil_annee}{C.RESET} — "
           f"Âge : {C.WHITE}{user.age or '?'}{C.RESET}")
        p()

        # Clubs actuels
        mes_adhesions = list(Adhesion.objects.filter(etudiant=user).select_related("club"))
        if mes_adhesions:
            pc(f"  {C.YELLOW}{C.BOLD}Mes clubs :{C.RESET}")
            for a in mes_adhesions:
                if a.statut == "ACCEPTEE":   st = f"{C.GREEN}Membre{C.RESET}"
                elif a.statut == "ATTENTE":  st = f"{C.YELLOW}En attente{C.RESET}"
                else:                        st = f"{C.RED}Refusée{C.RESET}"
                pc(f"    {C.CYAN}{a.club.nom}{C.RESET} — {st}")
            p()

        option("1", "Voir les clubs + Rejoindre")
        option("2", "Voir les événements + S'inscrire")
        option("3", "Se déconnecter")
        p()
        separateur()
        choix = saisir("Votre choix : ")

        if choix == "1":
            self._etudiant_clubs(user)
        elif choix == "2":
            self._etudiant_evenements(user)
        elif choix == "3":
            return False
        else:
            erreur("Option invalide."); pause()
        return True

    # ──────────────────────────────────────────
    def _etudiant_clubs(self, user):
        clear()
        sous_titre("Clubs disponibles", C.GREEN)
        clubs = list(Club.objects.filter(est_valide=True))
        if not clubs:
            info("Aucun club disponible."); pause(); return

        for c in clubs:
            adh = Adhesion.objects.filter(etudiant=user, club=c).first()
            if adh:
                if adh.statut == "ACCEPTEE":   badge = f" {C.GREEN}{C.BOLD}[MEMBRE]{C.RESET}"
                elif adh.statut == "ATTENTE":  badge = f" {C.YELLOW}[EN ATTENTE]{C.RESET}"
                else:                          badge = f" {C.RED}[REFUSÉE]{C.RESET}"
            else:
                badge = ""
            eligible, _ = c.verifier_etudiant(user)
            elig_badge = "" if eligible else f" {C.RED}[CONDITIONS NON REMPLIES]{C.RESET}"
            pc(f"  {C.WHITE}{C.BOLD}ID {c.id}{C.RESET} {C.DIM}|{C.RESET} "
               f"{C.CYAN}{C.BOLD}{c.nom}{C.RESET}{badge}{elig_badge}")
            pc(f"   {C.DIM}{c.description}{C.RESET}")
            afficher_conditions_club(c)
            separateur()

        p()
        cid = saisir("ID du club à rejoindre (ENTREE pour passer) : ")
        if cid:
            try:
                club = Club.objects.get(id=int(cid), est_valide=True)

                # ── Vérification des conditions ──────────────────────────
                ok, msg = club.verifier_etudiant(user)
                if not ok:
                    p()
                    erreur("Vous ne remplissez pas les conditions d'adhésion.")
                    erreur(msg)
                    pause()
                    return

                if Adhesion.objects.filter(etudiant=user, club=club).exists():
                    erreur("Vous avez déjà une demande pour ce club.")
                else:
                    Adhesion.objects.create(etudiant=user, club=club)
                    succes(f"Demande envoyée pour '{club.nom}' !")
            except (Club.DoesNotExist, ValueError):
                erreur("ID invalide.")
        pause()

    # ──────────────────────────────────────────
    def _etudiant_evenements(self, user):
        clear()
        sous_titre("Événements disponibles", C.GREEN)
        evts = list(Evenement.objects.select_related("club").all())
        if not evts:
            info("Aucun événement disponible."); pause(); return

        for e in evts:
            deja = Participation.objects.filter(etudiant=user, evenement=e).exists()
            badge = f" {C.GREEN}{C.BOLD}[INSCRIT]{C.RESET}" if deja else ""
            eligible, _ = e.verifier_etudiant(user)
            elig_badge = "" if eligible else f" {C.RED}[CONDITIONS NON REMPLIES]{C.RESET}"
            pc(f"  {C.WHITE}{C.BOLD}ID {e.id}{C.RESET} {C.DIM}|{C.RESET} "
               f"{C.CYAN}{C.BOLD}{e.titre}{C.RESET}{badge}{elig_badge}")
            pc(f"   {C.YELLOW}{e.date.strftime('%d/%m/%Y')}{C.RESET} "
               f"{C.DIM}|{C.RESET} {C.WHITE}{e.lieu}{C.RESET} "
               f"{C.DIM}| Club: {e.club.nom}{C.RESET}")
            afficher_conditions_event(e)
            separateur()

        p()
        eid = saisir("ID pour s'inscrire (ENTREE pour passer) : ")
        if eid:
            try:
                evt = Evenement.objects.get(id=int(eid))

                # ── Vérification des conditions ──────────────────────────
                ok, msg = evt.verifier_etudiant(user)
                if not ok:
                    p()
                    erreur("Vous ne remplissez pas les conditions de cet événement.")
                    erreur(msg)
                    pause()
                    return

                if Participation.objects.filter(etudiant=user, evenement=evt).exists():
                    erreur("Vous êtes déjà inscrit.")
                else:
                    Participation.objects.create(etudiant=user, evenement=evt)
                    succes(f"Inscrit à '{evt.titre}' !")
            except (Evenement.DoesNotExist, ValueError):
                erreur("ID invalide.")
        pause()
