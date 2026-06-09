# pyrefly: ignore [missing-import]
from django.shortcuts import render, get_object_or_404, redirect
# pyrefly: ignore [missing-import]
from django.contrib.auth.decorators import login_required
# pyrefly: ignore [missing-import]
from django.contrib import messages
from .models import Club, Adhesion
from .forms import ClubForm

def club_list(request):
    clubs = Club.objects.filter(est_valide=True)
    return render(request, 'clubs/club_list.html', {'clubs': clubs})

def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    deja_postule = False
    if request.user.is_authenticated and request.user.role == 'ETUDIANT':
        deja_postule = Adhesion.objects.filter(etudiant=request.user, club=club).exists()
    accepted_members_count = Adhesion.objects.filter(club=club, statut='ACCEPTEE').count()
    return render(request, 'clubs/club_detail.html', {
        'club': club,
        'deja_postule': deja_postule,
        'accepted_members_count': accepted_members_count,
    })

@login_required
def apply_to_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    if request.user.role != 'ETUDIANT':
        messages.error(request, "Seuls les étudiants peuvent postuler.")
        return redirect('club_detail', club_id=club.id)
        
    if Adhesion.objects.filter(etudiant=request.user, club=club).exists():
        messages.warning(request, "Vous avez déjà postulé à ce club.")
        return redirect('club_detail', club_id=club.id)
        
    eligible, erreur = club.verifier_etudiant(request.user)
    if not eligible:
        messages.error(request, f"Vous ne remplissez pas les conditions : {erreur}")
        return redirect('club_detail', club_id=club.id)
        
    Adhesion.objects.create(etudiant=request.user, club=club)
    messages.success(request, f"Votre demande d'adhésion au club {club.nom} a été envoyée avec succès !")
    return redirect('dashboard')

@login_required
def manage_adhesions(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user != club.responsable and request.user.role != 'ADMIN':
        messages.error(request, "Vous n'êtes pas autorisé à gérer ce club.")
        return redirect('home')
        
    adhesions = club.demandes_adhesion.all().order_by('-date_demande')
    return render(request, 'clubs/manage_adhesions.html', {'club': club, 'adhesions': adhesions})


@login_required
def club_members(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user != club.responsable and request.user.role != 'ADMIN':
        messages.error(request, "Accès refusé.")
        return redirect('home')

    members = club.demandes_adhesion.filter(statut='ACCEPTEE').select_related('etudiant').order_by('etudiant__username')
    return render(request, 'clubs/club_members.html', {'club': club, 'members': members})

@login_required
def approve_adhesion(request, adhesion_id):
    adhesion = get_object_or_404(Adhesion, id=adhesion_id)
    if request.user != adhesion.club.responsable and request.user.role != 'ADMIN':
        messages.error(request, "Accès refusé.")
        return redirect('home')
        
    adhesion.statut = 'ACCEPTEE'
    adhesion.save()
    messages.success(request, f"L'adhésion de {adhesion.etudiant.username} a été acceptée.")
    return redirect('manage_adhesions', club_id=adhesion.club.id)

@login_required
def reject_adhesion(request, adhesion_id):
    adhesion = get_object_or_404(Adhesion, id=adhesion_id)
    if request.user != adhesion.club.responsable and request.user.role != 'ADMIN':
        messages.error(request, "Accès refusé.")
        return redirect('home')
        
    adhesion.statut = 'REFUSEE'
    adhesion.save()
    messages.warning(request, f"L'adhésion de {adhesion.etudiant.username} a été refusée.")
    return redirect('manage_adhesions', club_id=adhesion.club.id)


@login_required
def remove_member(request, adhesion_id):
    adhesion = get_object_or_404(Adhesion, id=adhesion_id, statut='ACCEPTEE')
    if request.user != adhesion.club.responsable and request.user.role != 'ADMIN':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    if request.method != 'POST':
        return redirect('club_members', club_id=adhesion.club.id)

    club_id = adhesion.club.id
    username = adhesion.etudiant.username
    club_name = adhesion.club.nom
    adhesion.delete()
    messages.success(request, f"{username} t7yed men club {club_name}.")
    return redirect('club_members', club_id=club_id)

@login_required
def create_club(request):
    if request.user.role != 'RESPONSABLE':
        messages.error(request, "Ghir responsable y9der ycreer club.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES)
        if form.is_valid():
            club = form.save(commit=False)
            club.responsable = request.user
            club.save()
            messages.success(request, f"Le club {club.nom} a été créé avec succès et est en attente de validation.")
            return redirect('dashboard')
    else:
        form = ClubForm()
        
    return render(request, 'clubs/create_club.html', {'form': form})


@login_required
def edit_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user != club.responsable and request.user.role != 'ADMIN':
        messages.error(request, "Ma3andkch l7e9 tedit had club.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            form.save()
            messages.success(request, f"Les informations dyal {club.nom} tbedlo بنجاح.")
            return redirect('club_detail', club_id=club.id)
    else:
        form = ClubForm(instance=club)

    return render(request, 'clubs/create_club.html', {
        'form': form,
        'club': club,
        'is_edit': True,
    })

@login_required
def validate_club(request, club_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "Seuls les administrateurs peuvent valider un club.")
        return redirect('home')
        
    club = get_object_or_404(Club, id=club_id)
    club.est_valide = True
    club.save()
    messages.success(request, f"Le club {club.nom} a été validé avec succès.")
    return redirect('dashboard')


@login_required
def delete_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user != club.responsable and request.user.role != 'ADMIN':
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce club.")
        return redirect('home')
    if request.method != 'POST':
        return redirect('club_detail', club_id=club.id)

    club_name = club.nom
    club.delete()
    messages.success(request, f"Le club {club_name} tms7.")
    return redirect('dashboard')
