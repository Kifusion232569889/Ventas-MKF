#!/usr/bin/env python
"""
Prospección semanal — tabla "Centros y Terapeutas" (base MKF — Leads Prospección B2B).

Busca centros/terapeutas de kinesiología holística, biodescodificación,
constelaciones familiares, reiki y terapias holísticas en Barcelona,
deduplica contra Airtable y añade hasta 10 registros nuevos validados
(nombre + ciudad + teléfono/email/web como mínimo). Nunca inventa datos:
un campo sin dato confirmado se deja vacío.

Fuentes automatizadas (estáticas, sin JS, respetan robots.txt):
  - Doctoralia (listados de tratamiento/servicio en Barcelona)
  - Guía Consciente
  - InfoIsInfo Barcelona-provincia
  - Páginas Amarillas

Fuentes EXCLUIDAS de la automatización a propósito (decisión tomada al construir
este script, no un olvido):
  - Google Maps: scraping automatizado prohibido por sus Términos de Servicio.
    Alternativa: Google Places API (de pago) o búsqueda manual puntual.
  - airteas.org: sin listado público navegable de terapeutas en el momento
    de escribir este script; revisar manualmente si cambia.
Si se quiere cubrir Maps de forma legítima, hacerlo con la Places API, no
scrapeando el HTML de maps.google.com.

Uso:
    python prospecting_semanal.py

Requiere variables de entorno (ver .env.example):
    AIRTABLE_API_KEY, AIRTABLE_BASE_ID
"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from airtable_client import AirtableClient
from scraping_utils import extract_contacts, normalize, polite_get

load_dotenv()

TABLE_NAME = "Centros y Terapeutas"
TARGET_NEW = 10
LOG_FILE = os.path.join(os.path.dirname(__file__), "prospecting_log.txt")

# Nombres ya cargados manualmente antes de que existiera este script (sesión inicial).
SEED_DEDUPE = [
    "Institut de Salut Holística", "IGEM Institut Guxens", "INSTENAT",
    "Centro Kineos Barcelona", "IEKU Kinesiología Unificada", "Tara Salud Integral",
    "Escola General de Catalunya", "AMTH Reiki Barcelona", "Espai Vida Sant Joan Despí",
    "Hermes Cuida't i aprèn", "Mens Venilia", "Centro metro Girona", "Gemma Calaf",
    "Ybachi Terapias", "Carolina Zen", "Flor de Agua", "Guía Consciente",
]

DOCTORALIA_SOURCES = [
    ("https://www.doctoralia.es/tratamientos-servicios/kinesiologia-holistica/barcelona", "Kinesiología Holística"),
    ("https://www.doctoralia.es/tratamientos-servicios/biodescodificacion/barcelona", "Biodescodificación"),
    ("https://www.doctoralia.es/tratamientos-servicios/constelaciones-familiares/barcelona", "Constelaciones Familiares"),
]

GUIACONSCIENTE_SOURCE = "https://guiaconsciente.com/terapeutas/"
INFOISINFO_SOURCES = [
    ("https://barcelona-provincia.infoisinfo.es/busqueda/reiki", "Reiki"),
    ("https://barcelona-provincia.infoisinfo.es/busqueda/terapias+holisticas", "Terapias holísticas"),
]
PAGINASAMARILLAS_SOURCE = ("https://www.paginasamarillas.es/a/terapia-holistica/barcelona/", "Terapia holística")

DOCTORALIA_PROFILE_RE = re.compile(r"https://www\.doctoralia\.es/[a-z0-9-]+/[a-z0-9-]+/barcelona")


def log(msg: str) -> None:
    print(msg)


def append_log_summary(found: int, added: int, discarded: int, names_added: list[str]) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{dt.datetime.now().isoformat(timespec='seconds')}] "
                f"encontrados={found} nuevos_anadidos={added} descartados={discarded}\n")
        for n in names_added:
            f.write(f"  + {n}\n")


def candidates_from_doctoralia(dedupe: set[str], seen: set[str]) -> list[dict]:
    """Extrae nombre/ciudad/dirección/especialidad de listados Doctoralia.
    Doctoralia NO expone teléfono/email públicos (fuerza reserva por su plataforma):
    el enlace de perfil se usa como Fuente URL y, a falta de web propia, también como Web.
    """
    out = []
    for url, especialidad in DOCTORALIA_SOURCES:
        resp = polite_get(url)
        if resp is None:
            log(f"[doctoralia] no se pudo obtener {url} (robots.txt o error de red)")
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        for name_tag in soup.find_all(attrs={"itemprop": "name"}):
            name = name_tag.get_text(strip=True)
            if not name or normalize(name) in dedupe or normalize(name) in seen:
                continue
            link_tag = name_tag.find_parent("a") or name_tag.find_previous("a")
            profile_url = None
            if link_tag and link_tag.get("href"):
                href = link_tag["href"]
                if DOCTORALIA_PROFILE_RE.match(href):
                    profile_url = href
            if not profile_url:
                continue
            card = name_tag.find_parent(attrs={"class": "dp-doctor-card"}) or name_tag.parent
            street = card.find(attrs={"itemprop": "streetAddress"}) if card else None
            locality = card.find(attrs={"itemprop": "addressLocality"}) if card else None
            seen.add(normalize(name))
            out.append({
                "nombre": name,
                "tipo": "Terapeuta individual",
                "direccion": street.get("content", "") if street else "",
                "ciudad": (locality.get("content", "") if locality else "Barcelona") or "Barcelona",
                "especialidades": especialidad,
                "fuente_url": profile_url,
            })
    return out


def _generic_directory_candidates(url: str, especialidad: str, link_filter, dedupe: set[str], seen: set[str]) -> list[dict]:
    """Parser genérico best-effort para directorios sin microdatos: toma enlaces internos
    cuyo texto visible parece un nombre propio/comercial (heurística, no exacta).
    """
    resp = polite_get(url)
    if resp is None:
        log(f"[directorio] no se pudo obtener {url} (robots.txt o error de red)")
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        if not (3 <= len(text) <= 70):
            continue
        if not link_filter(href):
            continue
        if normalize(text) in dedupe or normalize(text) in seen:
            continue
        seen.add(normalize(text))
        out.append({
            "nombre": text,
            "tipo": "Centro",
            "ciudad": "Barcelona",
            "especialidades": especialidad,
            "fuente_url": href if href.startswith("http") else url,
            "detalle_url": href if href.startswith("http") else None,
        })
    return out


def candidates_from_guiaconsciente(dedupe: set[str], seen: set[str]) -> list[dict]:
    return _generic_directory_candidates(
        GUIACONSCIENTE_SOURCE, "Terapias holísticas",
        lambda href: "/terapeutas/" in href and href.rstrip("/") != GUIACONSCIENTE_SOURCE.rstrip("/"),
        dedupe, seen,
    )


def candidates_from_infoisinfo(dedupe: set[str], seen: set[str]) -> list[dict]:
    out = []
    for url, especialidad in INFOISINFO_SOURCES:
        out += _generic_directory_candidates(
            url, especialidad,
            lambda href: "infoisinfo.es" in href and "/busqueda/" not in href,
            dedupe, seen,
        )
    return out


def candidates_from_paginasamarillas(dedupe: set[str], seen: set[str]) -> list[dict]:
    url, especialidad = PAGINASAMARILLAS_SOURCE
    return _generic_directory_candidates(
        url, especialidad,
        lambda href: "paginasamarillas.es/f/" in href,
        dedupe, seen,
    )


def enrich_contact(candidate: dict) -> dict:
    """Intenta sacar teléfono/email/whatsapp visitando la web propia (o el perfil, si no hay otra)."""
    target_url = candidate.get("detalle_url") or candidate.get("fuente_url")
    if not target_url:
        return candidate
    resp = polite_get(target_url)
    if resp is None:
        return candidate
    contacts = extract_contacts(resp.text)
    candidate["telefono"] = contacts["telefono"]
    candidate["email"] = contacts["email"]
    candidate["whatsapp"] = f"https://wa.me/{contacts['whatsapp']}" if contacts["whatsapp"] else ""
    if not candidate.get("web") and target_url.startswith("http") and "doctoralia" not in target_url:
        candidate["web"] = target_url
    elif not candidate.get("web") and "doctoralia" in target_url:
        candidate["web"] = target_url  # perfil como único punto de contacto disponible
    return candidate


def meets_minimum(c: dict) -> bool:
    return bool(c.get("nombre")) and bool(c.get("ciudad")) and any(
        c.get(k) for k in ("telefono", "email", "web")
    )


def to_airtable_fields(c: dict) -> dict:
    return {
        "Nombre": c["nombre"],
        "Tipo": c.get("tipo", "Centro"),
        "Dirección": c.get("direccion", ""),
        "Ciudad": c.get("ciudad", "Barcelona"),
        "CP": c.get("cp", ""),
        "Teléfono": c.get("telefono", ""),
        "Email": c.get("email", ""),
        "WhatsApp": c.get("whatsapp", ""),
        "Web": c.get("web", ""),
        "Especialidades": c.get("especialidades", ""),
        "Alquila espacio": c.get("alquila_espacio", "N/D"),
        "Fuente URL": c.get("fuente_url", ""),
        "Fecha extracción": dt.date.today().isoformat(),
        "Estado": "Por contactar",
    }


def main() -> int:
    try:
        client = AirtableClient()
    except KeyError as e:
        log(f"ERROR: falta variable de entorno {e}. Copia .env.example a .env y rellénala.")
        return 1

    dedupe = client.existing_names(TABLE_NAME)
    dedupe |= {normalize(n) for n in SEED_DEDUPE}
    seen_this_run: set[str] = set()

    all_candidates: list[dict] = []
    for fetcher in (
        candidates_from_doctoralia,
        candidates_from_guiaconsciente,
        candidates_from_infoisinfo,
        candidates_from_paginasamarillas,
    ):
        if len([c for c in all_candidates if meets_minimum(c)]) >= TARGET_NEW * 2:
            break  # ya hay margen suficiente de candidatos, no seguir golpeando más fuentes
        all_candidates += fetcher(dedupe, seen_this_run)

    log(f"Candidatos brutos encontrados: {len(all_candidates)}")

    validated: list[dict] = []
    discarded = 0
    for c in all_candidates:
        if len(validated) >= TARGET_NEW:
            break
        c = enrich_contact(c)
        if meets_minimum(c):
            validated.append(c)
        else:
            discarded += 1

    if not validated:
        log("No se encontraron candidatos nuevos válidos en esta ejecución.")
        append_log_summary(len(all_candidates), 0, discarded, [])
        return 0

    records = [to_airtable_fields(c) for c in validated]
    created = client.create_records(TABLE_NAME, records)
    names_added = [c["nombre"] for c in validated]

    log(f"Añadidos {len(created)} registros nuevos a '{TABLE_NAME}'.")
    append_log_summary(len(all_candidates), len(created), discarded, names_added)
    return 0


if __name__ == "__main__":
    sys.exit(main())
