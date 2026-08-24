import json
import unicodedata
from datetime import UTC, datetime

from app.clients.provider_http import ProviderClientError, get_json
from app.core.config import settings


class ANEELClient:
    provider = "aneel"
    source_reference = "https://dadosabertos.aneel.gov.br/pt_BR/dataset/siga-sistema-de-informacoes-de-geracao-da-aneel"
    renewable_origins = {"HIDRICA", "EOLICA", "SOLAR", "BIOMASSA", "BIOGAS", "RESIDUOS"}

    @staticmethod
    def _number(value: object) -> float:
        if isinstance(value, int | float):
            return float(value)
        if not isinstance(value, str):
            return 0.0
        normalized = value.strip().replace(".", "").replace(",", ".")
        try:
            return float(normalized)
        except ValueError:
            return 0.0

    @staticmethod
    def _normalized_origin(value: object) -> str:
        if not isinstance(value, str):
            return ""
        return "".join(
            char for char in unicodedata.normalize("NFD", value.upper()) if unicodedata.category(char) != "Mn"
        )

    def get_energy_context(self, state_code: str | None) -> dict:
        state = (state_code or "").strip().upper()
        if len(state) != 2 or not state.isalpha():
            raise ProviderClientError(self.provider, "ANEEL requires a two-letter site state code")
        data, duration_ms = get_json(
            self.provider,
            settings.ANEEL_DATASTORE_URL,
            params={
                "resource_id": settings.ANEEL_SIGA_RESOURCE_ID,
                "limit": settings.ANEEL_MAX_RECORDS,
                "filters": json.dumps({"DscFaseUsina": "Operação", "SigUFPrincipal": state}),
            },
        )
        result = data.get("result")
        if not isinstance(result, dict):
            raise ProviderClientError(self.provider, "ANEEL returned an invalid datastore response")
        records = result.get("records")
        if not isinstance(records, list):
            raise ProviderClientError(self.provider, "ANEEL returned invalid generation records")
        try:
            total_records = int(result.get("total", len(records)))
        except (TypeError, ValueError):
            total_records = len(records)
        if total_records > len(records):
            raise ProviderClientError(
                self.provider,
                "ANEEL result exceeds ANEEL_MAX_RECORDS; increase the configured limit",
            )

        total_capacity_kw = 0.0
        renewable_capacity_kw = 0.0
        dataset_dates: list[str] = []
        for record in records:
            if not isinstance(record, dict):
                continue
            capacity_kw = self._number(
                record.get("MdaPotenciaFiscalizadaKw") or record.get("MdaPotenciaOutorgadaKw")
            )
            if capacity_kw <= 0:
                continue
            total_capacity_kw += capacity_kw
            if self._normalized_origin(record.get("DscOrigemCombustivel")) in self.renewable_origins:
                renewable_capacity_kw += capacity_kw
            dataset_date = record.get("DatGeracaoConjuntoDados")
            if isinstance(dataset_date, str):
                dataset_dates.append(dataset_date)

        if total_capacity_kw <= 0:
            raise ProviderClientError(self.provider, "ANEEL returned no usable installed capacity")
        observed_at = max(dataset_dates) if dataset_dates else datetime.now(UTC).date().isoformat()
        return {
            "payload": {
                "renewable_share": round(100 * renewable_capacity_kw / total_capacity_kw, 2),
                "installed_capacity_mw": round(total_capacity_kw / 1000, 3),
                "observed_at": observed_at,
                "dataset": "SIGA - Sistema de Informacoes de Geracao da ANEEL",
                "source_reference": self.source_reference,
                "state": state,
                "record_count": total_records,
                "scope": "Capacidade instalada em operacao no estado da unidade; nao representa geracao instantanea.",
            },
            "duration_ms": duration_ms,
            "collected_at": datetime.now(UTC).isoformat(),
        }
