"""
Test per src/load.py (fase LOAD).
Usiamo mock per non toccare mai il vero database durante i test.
"""
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from src.load import get_engine, load_to_database, upsert_to_database


SAMPLE_DF = pd.DataFrame([
    {"mal_id": 1, "title": "Cowboy Bebop", "score": 8.75},
    {"mal_id": 2, "title": "Naruto", "score": 7.9},
])


class TestGetEngine:

    @patch("src.load.DATABASE_URL", None)
    def test_solleva_errore_se_url_mancante(self):
        with pytest.raises(ValueError):
            get_engine()

    @patch("src.load.create_engine")
    @patch("src.load.DATABASE_URL", "postgresql://user:pass@host:5432/db")
    def test_crea_engine_con_timeout_di_connessione(self, mock_create_engine):
        get_engine()
        _, kwargs = mock_create_engine.call_args
        assert "connect_args" in kwargs
        assert kwargs["connect_args"].get("connect_timeout") == 10


class TestLoadToDatabase:

    def test_dataframe_vuoto_non_chiama_il_db(self):
        with patch("src.load.get_engine") as mock_get_engine:
            load_to_database(pd.DataFrame())
            mock_get_engine.assert_not_called()

    @patch("src.load.get_engine")
    def test_chiama_to_sql_con_parametri_corretti(self, mock_get_engine):
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine

        with patch.object(pd.DataFrame, "to_sql") as mock_to_sql:
            load_to_database(SAMPLE_DF, table_name="anime", if_exists="append")
            mock_to_sql.assert_called_once()
            _, kwargs = mock_to_sql.call_args
            assert kwargs["if_exists"] == "append"
            assert kwargs["index"] is False

        mock_engine.dispose.assert_called_once()


class TestUpsertToDatabase:

    def test_dataframe_vuoto_non_chiama_il_db(self):
        with patch("src.load.get_engine") as mock_get_engine:
            upsert_to_database(pd.DataFrame())
            mock_get_engine.assert_not_called()

    def test_solleva_errore_se_manca_colonna_chiave(self):
        df_senza_chiave = pd.DataFrame([{"title": "Naruto"}])
        with pytest.raises(ValueError):
            upsert_to_database(df_senza_chiave, key_column="mal_id")

    @patch("src.load.get_engine")
    def test_esegue_una_query_insert_per_riga(self, mock_get_engine):
        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        upsert_to_database(SAMPLE_DF, table_name="anime", key_column="mal_id")

        assert mock_conn.execute.call_count == len(SAMPLE_DF)
        mock_engine.dispose.assert_called_once()