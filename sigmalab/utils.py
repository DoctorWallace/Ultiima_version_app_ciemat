# sigmalab/utils.py
from django.db import models
from datetime import datetime

def generate_sample_code():
    """
    Genera un código de muestra único en formato YY-XXX
    Ejemplo: 25-001, 25-002, etc.
    """
    from .models import Solicitud
    
    # Obtener el año actual (últimos 2 dígitos)
    current_year = datetime.now().year % 100
    
    # Buscar el último código del año actual
    last_code = Solicitud.objects.filter(
        codigo_muestra__startswith=f"{current_year:02d}-"
    ).exclude(
        codigo_muestra__isnull=True
    ).exclude(
        codigo_muestra=""
    ).order_by('-codigo_muestra').first()
    
    if last_code and last_code.codigo_muestra:
        try:
            # Extraer el número del último código
            last_number = int(last_code.codigo_muestra.split('-')[1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            # Si hay error al parsear, empezar desde 1
            next_number = 1
    else:
        # Si no hay códigos del año actual, empezar desde 1
        next_number = 1
    
    # Formatear el código
    return f"{current_year:02d}-{next_number:03d}"

def assign_sample_code(solicitud):
    """
    Asigna un código de muestra a una solicitud si no lo tiene
    """
    if not solicitud.codigo_muestra:
        solicitud.codigo_muestra = generate_sample_code()
        solicitud.save(update_fields=['codigo_muestra'])
        return solicitud.codigo_muestra
    return solicitud.codigo_muestra

def get_sample_code_display(solicitud):
    """
    Obtiene el código de muestra para mostrar, generándolo si es necesario
    """
    if solicitud.codigo_muestra:
        return solicitud.codigo_muestra
    else:
        # Generar código pero no guardarlo hasta que se acepte la solicitud
        return generate_sample_code()