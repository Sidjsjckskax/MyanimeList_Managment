import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.config import MONITORING_LOG_PATH
from src.logger import setup_logger

logger = setup_logger(__name__)

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

        row = {
            "timestamp_inizio": self.start_time,
            "timestamp_fine": end_time,
            "durata_secondi": round(durata, 1),
            "record_estratti": self.record_estratti,
            "record_trasformati": self.record_trasformati,
            "record_caricati": self.record_caricati,
            "stato": stato,
            "errore": errore,
        }


        self._salva_csv(row)

    
        self._salva_db(row)

    def _salva_csv(self, row: dict):
        try:
            Path(MONITORING_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
            file_esiste = Path(MONITORING_LOG_PATH).exists()

            with open(MONITORING_LOG_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
                if not file_esiste:
                    writer.writeheader()

                csv_row = dict(row)
                csv_row["timestamp_inizio"] = row["timestamp_inizio"].strftime("%Y-%m-%d %H:%M:%S")
                csv_row["timestamp_fine"] = row["timestamp_fine"].strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow(csv_row)

        except OSError as e:
            logger.error(f"Impossibile scrivere il log CSV di monitoring: {e}")

    def _salva_db(self, row: dict):
    
        from src.load import get_engine

        try:
            engine = get_engine()
        except ValueError as e:
            logger.error(f"Impossibile salvare il monitoring su DB: {e}")
            return

        try:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO pipeline_runs
                            (timestamp_inizio, timestamp_fine, durata_secondi,
                             record_estratti, record_trasformati, record_caricati,
                             stato, errore)
                        VALUES
                            (:timestamp_inizio, :timestamp_fine, :durata_secondi,
                             :record_estratti, :record_trasformati, :record_caricati,
                             :stato, :errore)
                    """),
                    row,
                )
            logger.info("Esito pipeline salvato su database (tabella pipeline_runs)")

        except SQLAlchemyError as e:
            logger.error(f"Impossibile salvare il monitoring su database: {e}", exc_info=True)

        finally:
            engine.dispose()
