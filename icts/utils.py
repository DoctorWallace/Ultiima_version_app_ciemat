# icts/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import AccessProposal, ProposalReview

User = get_user_model()

def build_access_code(proposal, siglas):
    """Construye código de acceso único"""
    year = proposal.created_at.year
    return f"ICTS-{year}-{proposal.pk:04d}-{siglas}"

def generate_user_siglas(first_name, last_name):
    """Genera siglas del usuario"""
    if not first_name or not last_name:
        return "USER"
    
    # Tomar primeras letras de nombre y apellidos
    siglas = ""
    if first_name:
        siglas += first_name[0].upper()
    if last_name:
        # Tomar primeras letras de cada apellido
        apellidos = last_name.split()
        for apellido in apellidos[:2]:  # Máximo 2 apellidos
            if apellido:
                siglas += apellido[0].upper()
    
    return siglas[:4]  # Máximo 4 caracteres

def send_proposal_notification(proposal, action, recipient=None):
    """Envía notificación por email sobre cambios en propuestas"""
    if not settings.EMAIL_HOST_USER:
        return  # No enviar si no hay configuración de email
    
    context = {
        'proposal': proposal,
        'action': action,
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
    }
    
    if action == 'submitted':
        subject = f'Propuesta enviada: {proposal.title}'
        template = 'icts/emails/proposal_submitted.html'
        recipients = [proposal.applicant.email]
        
    elif action == 'review_assigned':
        subject = f'Nueva propuesta para revisar: {proposal.title}'
        template = 'icts/emails/review_assigned.html'
        # Enviar a todos los revisores
        reviewers = User.objects.filter(groups__name='revisores')
        recipients = [r.email for r in reviewers if r.email]
        
    elif action == 'review_completed':
        subject = f'Revisión completada: {proposal.title}'
        template = 'icts/emails/review_completed.html'
        recipients = [proposal.applicant.email]
        
    elif action == 'decision_made':
        subject = f'Decisión sobre propuesta: {proposal.title}'
        template = 'icts/emails/proposal_decision.html'
        recipients = [proposal.applicant.email]
        
    else:
        return
    
    if recipient:
        recipients = [recipient]
    
    try:
        html_message = render_to_string(template, context)
        send_mail(
            subject=subject,
            message='',  # Versión texto plano (opcional)
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception as e:
        # Log el error pero no fallar la aplicación
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error enviando email: {e}")

def send_user_approval_notification(user):
    """Envía notificación cuando un usuario es aprobado"""
    if not settings.EMAIL_HOST_USER or not user.email:
        return
        
    context = {
        'user': user,
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
    }
    
    try:
        html_message = render_to_string('icts/emails/user_approved.html', context)
        send_mail(
            subject='Cuenta aprobada - SIGMA ICTS',
            message='',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error enviando email de aprobación: {e}")