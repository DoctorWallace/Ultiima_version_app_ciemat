# icts/utils.py
import unicodedata
from typing import List

from .models import ICTSUserProfile


def _strip_accents(text: str) -> str:
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )


def _clean_alpha(text: str) -> str:
    text = _strip_accents(text).upper().strip()
    return "".join(ch for ch in text if ch.isalpha())


def generate_user_siglas(first_name: str, last_name: str) -> str:
    """Genera siglas únicas para el usuario.

    Regla:
    - Inicial del nombre + primera y última letra del primer apellido.
    - Si existe, y hay dos apellidos: inicial del nombre + inicial de ambos apellidos.
    - Si sigue existiendo: usar segunda, tercera, ... letra del primer apellido junto con la última.
    - Como último recurso, añadir un sufijo numérico incrementando desde 2.
    """
    fn = _clean_alpha(first_name) or "X"
    ln_clean = _clean_alpha(last_name) or "X"
    ln_parts = [p for p in _strip_accents(last_name).strip().split() if p]
    s1 = _clean_alpha(ln_parts[0]) if ln_parts else ln_clean
    s2 = _clean_alpha(ln_parts[1]) if len(ln_parts) > 1 else ""

    initial = fn[0]

    candidates: List[str] = []
    if len(s1) >= 1:
        first = s1[0]
        last = s1[-1]
        candidates.append((initial + first + last).upper())

    if s2:
        candidates.append((initial + s1[:1] + s2[:1]).upper())

    # Variaciones con letras internas del primer apellido
    for k in range(1, max(1, len(s1) - 1)):
        try:
            candidates.append((initial + s1[k] + s1[-1]).upper())
        except IndexError:
            break

    # Añadir sufijos numéricos si todo colisiona
    for base in list(candidates):
        for n in range(2, 100):
            candidates.append(f"{base}{n}")

    # Elegir primera no usada (case-insensitive)
    for cand in candidates:
        if not ICTSUserProfile.objects.filter(user_siglas__iexact=cand).exists():
            return cand

    # fallback improbable
    return candidates[0] if candidates else (initial + "XX")


def get_tech_acronyms_for_proposal(proposal) -> List[str]:
    """Construye la lista de siglas de técnicas solicitadas en un orden fijo.

    Orden: SIMS, SEM, FIB, CONF, VDG, ACEL, LML, OPT, IMP.
    Orígenes: booleanos del modelo y códigos del M2M `facilities`.
    """
    selected = set()

    # Desde booleanos
    if getattr(proposal, "facility_sims", False):
        selected.add("SIMS")
    if getattr(proposal, "facility_sem", False):
        selected.add("SEM")
    if getattr(proposal, "facility_sem_fib", False):
        selected.add("FIB")
    if getattr(proposal, "facility_confocal", False):
        selected.add("CONF")
    if getattr(proposal, "facility_vdg", False):
        selected.add("VDG")
    if getattr(proposal, "facility_imp", False):
        selected.add("ACEL")

    # Desde M2M facilities por código
    code_map = {
        "sims": "SIMS",
        "sem-edx": "SEM",
        "fib": "FIB",
        "confocal": "CONF",
        "van-der-graaff": "VDG",
        "implantador": "ACEL",
        "corrosion": "LML",
        "impedancia": "IMP",
        "optica": "OPT",
    }
    try:
        codes = list(proposal.facilities.values_list("code", flat=True))
        for c in codes:
            acro = code_map.get(str(c).lower())
            if acro:
                selected.add(acro)
    except Exception:
        pass

    order = ["SIMS", "SEM", "FIB", "CONF", "VDG", "ACEL", "LML", "OPT", "IMP"]
    return [a for a in order if a in selected]


def build_access_code(proposal, user_siglas: str) -> str:
    acros = get_tech_acronyms_for_proposal(proposal)
    prefix = "-".join(acros) if acros else "ICTS"
    code = f"{prefix}_{(user_siglas or '').upper()}".strip("_")
    return code[:50]

