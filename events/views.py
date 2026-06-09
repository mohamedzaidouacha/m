from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Evenement, Participation, EvenementImage
from clubs.models import Club
from .forms import EvenementForm
from datetime import date

def event_list(request):
    evenements = Evenement.objects.filter(date__gte=date.today()).order_by('date')
    return render(request, 'events/event_list.html', {'evenements': evenements})

def event_detail(request, event_id):
    event = get_object_or_404(Evenement, id=event_id)
    deja_inscrit = False
    if request.user.is_authenticated and request.user.role == 'ETUDIANT':
        deja_inscrit = Participation.objects.filter(etudiant=request.user, evenement=event).exists()
    
    participants_count = Participation.objects.filter(evenement=event).count()
        
    return render(request, 'events/event_detail.html', {
        'event': event, 
        'deja_inscrit': deja_inscrit,
        'participants_count': participants_count
    })

@login_required
def participate_event(request, event_id):
    event = get_object_or_404(Evenement, id=event_id)
    
    if request.user.role != 'ETUDIANT':
        messages.error(request, "Seuls les étudiants peuvent s'inscrire aux événements.")
        return redirect('event_detail', event_id=event.id)
        
    if Participation.objects.filter(etudiant=request.user, evenement=event).exists():
        messages.warning(request, "Vous êtes déjà inscrit à cet événement.")
        return redirect('event_detail', event_id=event.id)
        
    eligible, erreur = event.verifier_etudiant(request.user)
    if not eligible:
        messages.error(request, f"Vous ne remplissez pas les conditions : {erreur}")
        return redirect('event_detail', event_id=event.id)
        
    Participation.objects.create(etudiant=request.user, evenement=event)
    messages.success(request, f"Vous êtes maintenant inscrit à l'événement {event.titre} !")
    return redirect('dashboard')

@login_required
def create_event(request):
    if request.user.role != 'RESPONSABLE':
        messages.error(request, "Ghir responsable y9der ycreer événement.")
        return redirect('dashboard')
        
    clubs_geres = Club.objects.filter(responsable=request.user, est_valide=True)
    if not clubs_geres.exists():
        messages.error(request, "Vous ne gérez aucun club valide. Vous ne pouvez pas créer d'événement.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = EvenementForm(request.POST, request.FILES)
        club_id = request.POST.get('club')
        if form.is_valid() and club_id:
            club = get_object_or_404(Club, id=club_id, responsable=request.user)
            event = form.save(commit=False)
            event.club = club
            event.save()
            for image in request.FILES.getlist('galerie'):
                EvenementImage.objects.create(evenement=event, image=image)
            messages.success(request, f"L'événement {event.titre} a été créé avec succès !")
            return redirect('event_detail', event_id=event.id)
    else:
        form = EvenementForm()
        
    return render(request, 'events/create_event.html', {'form': form, 'clubs': clubs_geres})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Evenement.objects.select_related('club'), id=event_id)
    if request.user != event.club.responsable and request.user.role != 'ADMIN':
        messages.error(request, "Ma3andkch l7e9 tedit had l'événement.")
        return redirect('dashboard')

    clubs_geres = Club.objects.filter(responsable=request.user, est_valide=True)
    if request.user.role == 'ADMIN':
        clubs_geres = Club.objects.filter(id=event.club.id)

    if request.method == 'POST':
        form = EvenementForm(request.POST, request.FILES, instance=event)
        club_id = request.POST.get('club')
        if form.is_valid() and club_id:
            club = get_object_or_404(clubs_geres, id=club_id)
            updated_event = form.save(commit=False)
            updated_event.club = club
            updated_event.save()
            for image in request.FILES.getlist('galerie'):
                EvenementImage.objects.create(evenement=updated_event, image=image)
            messages.success(request, f"L'événement {updated_event.titre} tbedel بنجاح.")
            return redirect('event_detail', event_id=updated_event.id)
    else:
        form = EvenementForm(instance=event)

    return render(request, 'events/create_event.html', {
        'form': form,
        'clubs': clubs_geres,
        'event': event,
        'is_edit': True,
    })


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Evenement.objects.select_related('club'), id=event_id)
    if request.user != event.club.responsable and request.user.role != 'ADMIN':
        messages.error(request, "Ma3andkch l7e9 tms7 had l'événement.")
        return redirect('dashboard')
    if request.method != 'POST':
        return redirect('event_detail', event_id=event.id)

    event_title = event.titre
    event.delete()
    messages.success(request, f"L'événement {event_title} tms7.")
    return redirect('dashboard')


@login_required
def event_participants(request, event_id):
    event = get_object_or_404(Evenement.objects.select_related('club'), id=event_id)
    if request.user != event.club.responsable and request.user.role != 'ADMIN':
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')

    participants = event.participants.select_related('etudiant').order_by('etudiant__username')
    return render(request, 'events/event_participants.html', {
        'event': event,
        'participants': participants,
    })
