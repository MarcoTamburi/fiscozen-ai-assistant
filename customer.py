import pandas as pd
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CustomerProfile:
    nome: str
    cognome: str
    regime: str
    cassa: str
    commercialista: str
    apertura_piva: str
    fatturato_2025: float
    fatturato_2026: float

    @property
    def full_name(self) -> str:
        return f"{self.nome} {self.cognome}"

    @property
    def is_sanitario(self) -> bool:
        """I sanitari possono emettere fatture cartacee."""
        return self.cassa in ("ENPAP", "ENPAM", "ENPAPI")

    @property
    def is_forfettario(self) -> bool:
        return self.regime.lower() == "forfettario"

    @property
    def fatturato_corrente(self) -> float:
        """Fatturato dell'anno in corso (2026)."""
        return self.fatturato_2026

    @property
    def soglia_rimanente(self) -> float | None:
        """Margine al limite forfettario (85k€). None se non forfettario."""
        if not self.is_forfettario:
            return None
        return 85.0 - self.fatturato_corrente

    def to_context_string(self) -> str:
        """Stringa di contesto da iniettare nel prompt."""
        lines = [
            f"- Nome: {self.full_name}",
            f"- Regime fiscale: {self.regime}",
            f"- Cassa previdenziale: {self.cassa}",
            f"- Commercialista assegnato: {self.commercialista}",
            f"- Apertura P.IVA: {self.apertura_piva}",
            f"- Fatturato 2025: {self.fatturato_2025}k€",
            f"- Fatturato 2026 (progressivo): {self.fatturato_corrente}k€",
        ]
        if self.is_forfettario:
            rimanente = self.soglia_rimanente
            lines.append(
                f"- Margine al limite forfettario (85k€): {rimanente:.1f}k€"
            )
        if self.is_sanitario:
            lines.append(
                "- Può emettere fatture cartacee (iscritto a cassa sanitaria)"
            )
        return "\n".join(lines)


class CustomerRepository:
    def __init__(self, excel_path: str = "data/customer_data.xlsx"):
        self._df = pd.read_excel(excel_path, dtype=str)
        self._df.columns = [c.strip().lower() for c in self._df.columns]
        self._customers: dict[str, CustomerProfile] = {}
        self._parse()

    def _parse(self):
        for _, row in self._df.iterrows():
            raw_apertura = str(row.get("apertura_piva", "")).strip()
            try:
                anno = str(pd.to_datetime(raw_apertura, dayfirst=False).year)
            except Exception:
                anno = raw_apertura[:4] if len(raw_apertura) >= 4 else raw_apertura

            profile = CustomerProfile(
                nome=str(row.get("nome", "")).strip(),
                cognome=str(row.get("cognome", "")).strip(),
                regime=str(row.get("regime", "")).strip(),
                cassa=str(row.get("cassa", "")).strip(),
                commercialista=str(row.get("commercialista", "")).strip(),
                apertura_piva=anno,
                fatturato_2025=float(row.get("fatturato_2025", 0) or 0),
                fatturato_2026=float(row.get("fatturato_2026", 0) or 0),
            )
            key = profile.full_name.lower().replace(" ", "_")
            self._customers[key] = profile

    def get_all(self) -> list[CustomerProfile]:
        return list(self._customers.values())

    def get_by_name(self, name: str) -> CustomerProfile | None:
        key = name.lower().replace(" ", "_")
        return self._customers.get(key)

    def get_display_names(self) -> list[str]:
        return [c.full_name for c in self.get_all()]
