# pyrefly: ignore [missing-import]
from django.shortcuts import render, redirect, get_object_or_404
# pyrefly: ignore [missing-import]
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Count, Q
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404
from django.utils import timezone
from accounts.models import Utilisateur
from clubs.models import Club, Adhesion
from events.models import Evenement, Participation
from datetime import date, datetime
import os


def home(request):
    if request.user.is_authenticated and request.user.role in {'ADMIN', 'RESPONSABLE'}:
        return redirect('dashboard')
    clubs = Club.objects.filter(est_valide=True).order_by('-date_creation')[:3]
    evenements = Evenement.objects.filter(date__gte=date.today()).order_by('date')[:3]
    return render(request, 'core/index.html', {
        'clubs': clubs,
        'evenements': evenements,
    })


def _uploads_storage() -> FileSystemStorage:
    return FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, 'uploads'),
        base_url=f"{settings.MEDIA_URL}uploads/",
    )


def _require_admin_or_responsable(user) -> bool:
    return getattr(user, 'role', None) in {'ADMIN', 'RESPONSABLE'}


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def _list_managed_files():
    storage = _uploads_storage()
    os.makedirs(storage.location, exist_ok=True)

    files = []
    for entry in os.scandir(storage.location):
        if not entry.is_file():
            continue
        stat = entry.stat()
        modified_at = timezone.localtime(datetime.fromtimestamp(stat.st_mtime, tz=timezone.get_current_timezone()))
        files.append({
            'name': entry.name,
            'url': storage.url(entry.name),
            'size_bytes': stat.st_size,
            'size_display': _format_size(stat.st_size),
            'modified_display': modified_at.strftime('%d/%m/%Y %H:%M'),
        })

    files.sort(key=lambda x: x['name'].lower())
    return files


@login_required
def dashboard(request):
    user = request.user
    if user.role == 'ADMIN':
        clubs_attente = Club.objects.filter(est_valide=False).select_related('responsable')
        tous_clubs = Club.objects.select_related('responsable').annotate(
            accepted_members_count=Count('demandes_adhesion', filter=Q(demandes_adhesion__statut='ACCEPTEE')),
            pending_requests_count=Count('demandes_adhesion', filter=Q(demandes_adhesion__statut='ATTENTE')),
        )
        evenements = Evenement.objects.select_related('club').all()
        context = {
            'clubs_attente': clubs_attente,
            'tous_clubs': tous_clubs,
            'evenements': evenements,
            'users_count': Utilisateur.objects.count(),
            'banned_count': Utilisateur.objects.filter(is_active=False).count(),
        }
    elif user.role == 'RESPONSABLE':
        clubs_geres = Club.objects.filter(responsable=user).annotate(
            accepted_members_count=Count('demandes_adhesion', filter=Q(demandes_adhesion__statut='ACCEPTEE')),
            pending_requests_count=Count('demandes_adhesion', filter=Q(demandes_adhesion__statut='ATTENTE')),
        )
        evenements = Evenement.objects.filter(club__in=clubs_geres)
        context = {
            'clubs_geres': clubs_geres,
            'evenements': evenements,
        }
    else:
        mes_adhesions = Adhesion.objects.filter(etudiant=user).select_related('club').order_by('-date_demande')
        participations = Participation.objects.filter(etudiant=user).select_related('evenement', 'evenement__club').order_by('-date_inscription')
        context = {
            'mes_adhesions': mes_adhesions,
            'participations': participations,
        }

    if _require_admin_or_responsable(user):
        context['managed_files'] = _list_managed_files()
        context['max_upload_size_mb'] = 10

    return render(request, 'core/dashboard.html', context)


@login_required
def upload_managed_file(request):
    if not _require_admin_or_responsable(request.user):
        raise Http404
    if request.method != 'POST':
        return redirect('dashboard')

    uploaded = request.FILES.get('file')
    if not uploaded:
        messages.error(request, "Choisi un fichier 3afak.")
        return redirect('dashboard')

    max_size = 10 * 1024 * 1024
    if uploaded.size > max_size:
        messages.error(request, "Had fichier kbir بزاف. الحد الأقصى هو 10MB.")
        return redirect('dashboard')

    allowed_extensions = {
        '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.webp',
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.txt', '.zip', '.rar',
    }
    _, ext = os.path.splitext(uploaded.name.lower())
    if ext and ext not in allowed_extensions:
        messages.error(request, "نوع ديال fichier ما مسموحش به.")
        return redirect('dashboard')

    storage = _uploads_storage()
    os.makedirs(storage.location, exist_ok=True)
    saved_name = storage.save(os.path.basename(uploaded.name), uploaded)
    messages.success(request, f"Fichier tرفع: {saved_name}")
    return redirect('dashboard')


@login_required
def delete_managed_file(request, filename: str):
    if not _require_admin_or_responsable(request.user):
        raise Http404
    if request.method != 'POST':
        return redirect('dashboard')

    if filename != os.path.basename(filename):
        raise Http404

    storage = _uploads_storage()
    if not storage.exists(filename):
        messages.warning(request, "Had fichier ma بقىش كاين.")
        return redirect('dashboard')

    storage.delete(filename)
    messages.success(request, f"Fichier tms7: {filename}")
    return redirect('dashboard')


@login_required
def download_managed_file(request, filename: str):
    if not _require_admin_or_responsable(request.user):
        raise Http404

    if filename != os.path.basename(filename):
        raise Http404

    storage = _uploads_storage()
    if not storage.exists(filename):
        raise Http404

    file_handle = storage.open(filename, mode='rb')
    return FileResponse(file_handle, as_attachment=True, filename=os.path.basename(filename))


@login_required
def admin_users(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Seul ladmin y9der ychouf had page.")
        return redirect('dashboard')

    users = Utilisateur.objects.order_by('role', 'username')
    context = {
        'users': users,
        'users_count': users.count(),
        'students_count': users.filter(role='ETUDIANT').count(),
        'responsables_count': users.filter(role='RESPONSABLE').count(),
        'banned_count': users.filter(is_active=False).count(),
    }
    return render(request, 'core/admin_users.html', context)


@login_required
def ban_user(request, user_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "Seul ladmin y9der ybanne users.")
        return redirect('dashboard')
    if request.method != 'POST':
        return redirect('admin_users')

    target_user = get_object_or_404(Utilisateur, id=user_id)
    if target_user == request.user:
        messages.error(request, "Ma9derch tbanne rassek.")
    elif target_user.role == 'ADMIN':
        messages.error(request, "Ma9derch tbanne admin akhor.")
    elif not target_user.is_active:
        messages.warning(request, "Had user deja mabanni.")
    else:
        target_user.is_active = False
        target_user.save(update_fields=['is_active'])
        messages.success(request, f"{target_user.username} tbanne بنجاح.")
    return redirect('admin_users')


@login_required
def unban_user(request, user_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "Seul ladmin y9der y7yed ban.")
        return redirect('dashboard')
    if request.method != 'POST':
        return redirect('admin_users')

    target_user = get_object_or_404(Utilisateur, id=user_id)
    if target_user.is_active:
        messages.warning(request, "Had user deja actif.")
    else:
        target_user.is_active = True
        target_user.save(update_fields=['is_active'])
        messages.success(request, f"{target_user.username} rja3 actif.")
    return redirect('admin_users')


@login_required
def delete_account(request):
    if request.method != 'POST':
        return redirect('dashboard')

    user = request.user
    username = user.username
    logout(request)
    user.delete()
    messages.success(request, f"Lcompte dyalk {username} tms7.")
    return redirect('home')
