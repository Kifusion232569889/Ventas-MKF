"""Cliente mínimo de la API REST de Airtable (solo requests, sin SDK)."""
import os
import time

import requests

from scraping_utils import normalize

AIRTABLE_API_URL = "https://api.airtable.com/v0"


class AirtableClient:
    def __init__(self, api_key: str | None = None, base_id: str | None = None):
        self.api_key = api_key or os.environ["AIRTABLE_API_KEY"]
        self.base_id = base_id or os.environ["AIRTABLE_BASE_ID"]
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def existing_names(self, table_name: str, name_field: str = "Nombre") -> set[str]:
        """Nombres (normalizados) ya presentes en una tabla, para deduplicar."""
        names: set[str] = set()
        offset = None
        url = f"{AIRTABLE_API_URL}/{self.base_id}/{table_name}"
        while True:
            params = {"fields[]": name_field, "pageSize": 100}
            if offset:
                params["offset"] = offset
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            for rec in data.get("records", []):
                val = rec.get("fields", {}).get(name_field)
                if val:
                    names.add(normalize(val))
            offset = data.get("offset")
            if not offset:
                break
        return names

    def create_records(self, table_name: str, records: list[dict], typecast: bool = True) -> list[dict]:
        """records: lista de dicts {nombre_campo: valor}. Inserta en bloques de 10."""
        url = f"{AIRTABLE_API_URL}/{self.base_id}/{table_name}"
        created = []
        for i in range(0, len(records), 10):
            chunk = records[i:i + 10]
            payload = {"records": [{"fields": r} for r in chunk], "typecast": typecast}
            resp = self.session.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            created.extend(resp.json().get("records", []))
            time.sleep(0.3)
        return created
