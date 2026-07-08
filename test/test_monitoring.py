from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.monitoring import PipelineRunMonitor


@pytest.fixture
def monitoring_csv_path(tmp_path):
    fake_path = tmp_path / "monitoring.csv"
    with patch("src.monitoring.MONITORING_LOG_PATH", str(fake_path)):
        yield fake_path


class TestPipelineRunMonitor:

    @patch("src.load.get_engine")
    def test_salva_successo_scrive_csv_e_db(self, mock_get_engine, monitoring_csv_path):
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine

        monitor = PipelineRunMonitor()
        monitor.set_estratti(10)
        monitor.set_trasformati(10)
        monitor.set_caricati(10)
        monitor.salva_successo()

        # CSV scritto correttamente
        assert monitoring_csv_path.exists()
        contenuto = monitoring_csv_path.read_text(encoding="utf-8")
        assert "SUCCESSO" in contenuto
        assert "10" in contenuto

        # Riga inserita nel DB tramite l'engine mockato
        mock_engine.begin.assert_called_once()
        mock_engine.dispose.assert_called_once()

    @patch("src.load.get_engine")
    def test_salva_fallimento_registra_messaggio_errore(self, mock_get_engine, monitoring_csv_path):
        mock_get_engine.return_value = MagicMock()

        monitor = PipelineRunMonitor()
        monitor.salva_fallimento(Exception("Fallito dopo 3 tentativi"))

        contenuto = monitoring_csv_path.read_text(encoding="utf-8")
        assert "FALLITO" in contenuto
        assert "Fallito dopo 3 tentativi" in contenuto

    @patch("src.load.get_engine")
    def test_errore_db_non_blocca_il_salvataggio_csv(self, mock_get_engine, monitoring_csv_path):
        mock_engine = MagicMock()
        mock_engine.begin.side_effect = SQLAlchemyError("connessione rifiutata")
        mock_get_engine.return_value = mock_engine

        monitor = PipelineRunMonitor()
        monitor.salva_successo()  

        assert monitoring_csv_path.exists()

    @patch("src.load.get_engine", side_effect=ValueError("DATABASE_URL non impostata nel .env"))
    def test_database_url_mancante_non_blocca_il_salvataggio_csv(self, mock_get_engine, monitoring_csv_path):
        monitor = PipelineRunMonitor()
        monitor.salva_successo() 

        assert monitoring_csv_path.exists()
