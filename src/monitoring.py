import csv
from datetime import datetime
from pathlib import Path

from src.config import MONITORING_LOG_PATH

_FIELDNAMES = [
    "timestamp_inizio",
    "timestamp_fine",
    "durata_secondi",
    "record_estratti",
    "record_trasformati",
    "record_caricati",
    "stato",
    "errore",
]


class PipelineRunMonitor:

    def __init__(self):
        self.start_time = datetime.now()
        self.record_estratti = 0
        self.record_trasformati = 0
        self.record_caricati = 0

    def set_estratti(self, n: int):
        self.record_estratti = n

    def set_trasformati(self, n: int):
        self.record_trasformati = n

    def set_caricati(self, n: int):
        self.record_caricati = n

    def salva_successo(self):
        self._salva(stato="SUCCESSO", errore="")

    def salva_fallimento(self, errore: Exception):
        self._salva(stato="FALLITO", errore=str(errore))

    def _salva(self, stato: str, errore: str):
        end_time = datetime.now()
        durata = (end_time - self.start_time).total_seconds()

        Path(MONITORING_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
        file_esiste = Path(MONITORING_LOG_PATH).exists()

        with open(MONITORING_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
            if not file_esiste:
                writer.writeheader()

            writer.writerow({
                "timestamp_inizio": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp_fine": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "durata_secondi": round(durata, 1),
                "record_estratti": self.record_estratti,
                "record_trasformati": self.record_trasformati,
                "record_caricati": self.record_caricati,
                "stato": stato,
                "errore": errore,
            })