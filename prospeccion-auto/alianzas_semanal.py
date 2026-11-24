#!/usr/bin/env python
"""
Prospección semanal de ALIANZAS ESTRATÉGICAS — tabla "Aliados Estratégicos"
(base MKF — Leads Prospección B2B).

Busca profesionales/centros de disciplinas afines (acupuntura, flores de Bach,
constelaciones, psicología integrativa, coaching emocional, fisioterapia
holística, nutrición emocional, yoga, estética premium, medicina ancestral)
en Barcelona, deduplica contra AMBAS tablas de la base (Centros y Terapeutas +
Aliados Estratégicos) y añade hasta 10 registros nuevos validados.
Nunca inventa datos: campo sin dato confirmado = vacío.

Fuentes automatizadas: Doctoralia (categorías con slug confirmado) e
InfoIsInfo Barcelona-provincia (búsqueda genérica por término).

Fuentes EXCLUIDAS de la automatización a propósito:
  - Google Maps: scraping prohibido por sus Términos de Servicio.
  - Instagram / LinkedIn (hashtags, búsquedas): requieren sesión autenticada,
    scrapearlos rompe sus ToS y dispara detección anti-bot agresiva
    (especialmente LinkedIn). Si se quiere automatizar de verdad, usar la
    Graph API oficial de Meta o la API de LinkedIn con las credenciales
    correspondientes — no un scraper con evasión de detección.
  Ambas quedan como tarea manual puntual, no como parte de este cron.

Uso:
    python alianzas_semanal.py

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
from scraping_utils import extract_contacts, extract_social, normalize, polite_get

load_dotenv()

TABLE_NAME = "Aliados Estratégicos"
CENTROS_TABLE_NAME = "Centros y Terapeutas"
TARGET_NEW = 10
LOG_FILE = os.path.join(os.path.dirname(__file__), "alianzas_log.txt")

DOCTORALIA_PROFILE_RE = re.compile(r"https://www\.doctoralia\.es/[a-z0-9-]+/[a-z0-9-]+/barcelona")

# (categoría exacta de Airtable, fit MKF, slug doctoralia o None, término infoisinfo o None)
CATEGORIES = [
    ("Acupuntura y MTC", "Alto", "acupuntura", "acupuntura"),
    ("Flores de Bach y terapia floral", "Alto", "terapia-con-flores-de-bach", "flores+de+bach"),
    ("Constelaciones familiares", "Alto", None, "constelaciones+familiares"),
    ("Psicólogos con enfoque integrativo", "Alto", "terapia-con-emdr", None),
    ("Coaches de vida con base emocional", "Alto", None, "coach+emocional"),
    ("Médicos y fisioterapeutas con visión holística", "Medio", None, "fisioterapia+holistica"),
    ("Nutricionistas con enfoque emocional", "Medio", None, "nutricionista"),
    ("Yoga y meditación (estudios)", "Medio", None, "yoga"),
    ("Centros de estética y bienestar premium", "Medio", None, "centro+de+estetica"),
    ("Medicina ancestral y chamánica", "Alto", None, "chaman"),
]

COLABORACION_POR_FIT = {
    "Alto": "Derivación bidireccional: bloqueos emocionales profundos → MKF; necesidad de su especialidad → aliado. Candidato a Certificación Basic.",
    "Medio": "Colaboración puntual: talleres/eventos conjuntos, derivación cuando el origen del caso es emocional.",
    "Bajo": "Explorar colaboración de comunidad (eventos, contenido conjunto) antes de derivación directa.",
}


def log(msg: str) -> None:
    print(msg)


def append_log_summary(found: int, added: int, discarded: int, added_detail: list[tuple[str, str]]) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{dt.datetime.now().isoformat(timespec='seconds')}] "
                f"encontrados={found} nuevos_anadidos={added} descartados={discarded}\n")
        for nombre, categoria in added_detail:
            f.write(f"  + {nombre}  [{categoria}]\n")


def candidates_from_doctoralia(slug: str, categoria: str, fit: str, dedupe: set[str], seen: set[str]) -> list[dict]:
    url = f"https://www.doctoralia.es/tratamientos-servicios/{slug}/barcelona"
    resp = polite_get(url)
    if resp is None:
        log(f"[doctoralia] sin resultado para {url}")
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    out = []
    for name_tag in soup.find_all(attrs={"itemprop": "name"}):
        name = name_tag.get_text(strip=True)
        if not name or normalize(name) in dedupe or normalize(name) in seen:
            continue
        link_tag = name_tag.find_parent("a") or name_tag.find_previous("a")
        if not (link_tag and link_tag.get("href") and DOCTORALIA_PROFILE_RE.match(link_tag["href"])):
            continue
        profile_url = link_tag["href"]
        card = name_tag.find_parent(attrs={"class": "dp-doctor-card"}) or name_tag.parent
        street = card.find(attrs={"itemprop": "streetAddress"}) if card else None
        locality = card.find(attrs={"itemprop": "addressLocality"}) if card else None
        seen.add(normalize(name))
        out.append({
            "nombre": name,
            "categoria": categoria,
            "fit": fit,
            "direccion": street.get("content", "") if street else "",
            "ciudad": (locality.get("content", "") if locality else "Barcelona") or "Barcelona",
            "especialidad": categoria,
            "fuente_url": profile_url,
        })
    return out


def candidates_from_infoisinfo(term: str, categoria: str, fit: str, dedupe: set[str], seen: set[str]) -> list[dict]:
    url = f"https://barcelona-provincia.infoisinfo.es/busqueda/{term}"
    resp = polite_get(url)
    if resp is None:
        log(f"[infoisinfo] sin resultado para {url}")
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        if not (3 <= len(text) <= 70) or "infoisinfo.es" not in href or "/busqueda/" in href:
            continue
        if normalize(text) in dedupe or normalize(text) in seen:
            continue
        seen.add(normalize(text))
        out.append({
            "nombre": text,
            "categoria": categoria,
            "fit": fit,
            "ciudad": "Barcelona",
            "especialidad": categoria,
            "fuente_url": href,
            "detalle_url": href,
        })
    return out


def enrich_contact(candidate: dict) -> dict:
    target_url = candidate.get("detalle_url") or candidate.get("fuente_url")
    if not target_url:
        return candidate
    resp = polite_get(target_url)
    if resp is None:
        return candidate
    contacts = extract_contacts(resp.text)
    social = extract_social(resp.text)
    candidate["telefono"] = contacts["telefono"]
    candidate["email"] = contacts["email"]
    candidate["whatsapp"] = f"https://wa.me/{contacts['whatsapp']}" if contacts["whatsapp"] else ""
    candidate["instagram_linkedin"] = social["instagram"] or social["linkedin"]
    if target_url.startswith("http"):
        candidate["web"] = target_url
    return candidate


def meets_minimum(c: dict) -> bool:
    return bool(c.get("nombre")) and bool(c.get("ciudad")) and any(
        c.get(k) for k in ("telefono", "email", "instagram_linkedin")
    )


def to_airtable_fields(c: dict) -> dict:
    return {
        "Nombre": c["nombre"],
        "Tipo de aliado": c["categoria"],
        "Especialidad": c.get("especialidad", ""),
        "Dirección": c.get("direccion", ""),
        "Ciudad": c.get("ciudad", "Barcelona"),
        "Teléfono": c.get("telefono", ""),
        "Email": c.get("email", ""),
        "WhatsApp": c.get("whatsapp", ""),
        "Web": c.get("web", ""),
        "Instagram / LinkedIn": c.get("instagram_linkedin", ""),
        "Nivel de fit con MKF": c.get("fit", "Medio"),
        "Tipo de colaboración propuesta": COLABORACION_POR_FIT.get(c.get("fit", "Medio"), ""),
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

    dedupe = client.existing_names(TABLE_NAME) | client.existing_names(CENTROS_TABLE_NAME)
    seen_this_run: set[str] = set()

    all_candidates: list[dict] = []
    for categoria, fit, slug, term in CATEGORIES:
        if len([c for c in all_candidates if meets_minimum(c)]) >= TARGET_NEW * 2:
            break
        if slug:
            all_candidates += candidates_from_doctoralia(slug, categoria, fit, dedupe, seen_this_run)
        if term:
            all_candidates += candidates_from_infoisinfo(term, categoria, fit, dedupe, seen_this_run)

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
        log("No se encontraron aliados nuevos válidos en esta ejecución.")
        append_log_summary(len(all_candidates), 0, discarded, [])
        return 0

    records = [to_airtable_fields(c) for c in validated]
    created = client.create_records(TABLE_NAME, records)
    added_detail = [(c["nombre"], c["categoria"]) for c in validated]

    log(f"Añadidos {len(created)} registros nuevos a '{TABLE_NAME}'.")
    append_log_summary(len(all_candidates), len(created), discarded, added_detail)
    return 0


if __name__ == "__main__":
    sys.exit(main())
