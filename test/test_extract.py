"""
Test per src/jikan.py (fase EXTRACT).
Usiamo mock per non fare vere chiamate all'API Jikan durante i test.
"""
import json
from unittest.mock import patch, MagicMock

import pytest
import requests

from src.jikan import fetch_with_retry, fetch_anime_page, extract_all_anime, save_raw_data


def _fake_response(json_data, status_code=200):
    """Crea una finta risposta requests.Response"""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
    return resp


class TestFetchWithRetry:

    @patch("src.jikan.requests.get")
    def test_successo_al_primo_tentativo(self, mock_get):
        mock_get.return_value = _fake_response({"data": []})
        result = fetch_with_retry("http://fake-url", {})
        assert result == {"data": []}
        assert mock_get.call_count == 1

    @patch("src.jikan.time.sleep", return_value=None)  # niente attese reali nei test
    @patch("src.jikan.requests.get")
    def test_rate_limit_429_poi_successo(self, mock_get, mock_sleep):
        mock_get.side_effect = [
            _fake_response({}, status_code=429),
            _fake_response({"data": [{"mal_id": 1}]}),
        ]
        result = fetch_with_retry("http://fake-url", {}, max_retries=3)
        assert result == {"data": [{"mal_id": 1}]}
        assert mock_get.call_count == 2

    @patch("src.jikan.time.sleep", return_value=None)
    @patch("src.jikan.requests.get")
    def test_fallisce_dopo_max_retries(self, mock_get, mock_sleep):
        mock_get.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(requests.exceptions.RequestException):
            fetch_with_retry("http://fake-url", {}, max_retries=2)
        assert mock_get.call_count == 2


class TestFetchAnimePage:

    @patch("src.jikan.fetch_with_retry")
    def test_costruisce_url_e_parametri_corretti(self, mock_fetch):
        mock_fetch.return_value = {"data": []}
        fetch_anime_page(3)
        args, kwargs = mock_fetch.call_args
        assert args[0].endswith("/anime")
        assert args[1] == {"page": 3, "limit": 25}


class TestExtractAllAnime:

    @patch("src.jikan.time.sleep", return_value=None)
    @patch("src.jikan.fetch_anime_page")
    def test_si_ferma_quando_non_ce_piu_pagina_successiva(self, mock_fetch, mock_sleep):
        mock_fetch.side_effect = [
            {"data": [{"mal_id": 1}, {"mal_id": 2}], "pagination": {"has_next_page": True}},
            {"data": [{"mal_id": 3}], "pagination": {"has_next_page": False}},
        ]
        result = extract_all_anime(max_pages=10)
        assert len(result) == 3
        assert mock_fetch.call_count == 2

    @patch("src.jikan.fetch_anime_page")
    def test_si_ferma_su_pagina_vuota(self, mock_fetch):
        mock_fetch.return_value = {"data": [], "pagination": {"has_next_page": True}}
        result = extract_all_anime(max_pages=5)
        assert result == []

    @patch("src.jikan.fetch_anime_page")
    def test_si_ferma_su_errore_di_rete_senza_sollevare_eccezione(self, mock_fetch):
        mock_fetch.side_effect = requests.exceptions.RequestException("errore simulato")
        result = extract_all_anime(max_pages=5)
        assert result == []  # estrazione interrotta ma nessun crash


class TestSaveRawData:

    def test_salva_file_json_e_ritorna_path(self, tmp_path, monkeypatch):
        import src.jikan as jikan_module
        monkeypatch.setattr(jikan_module, "RAW_DATA_PATH", str(tmp_path))

        data = [{"mal_id": 1, "title": "Test Anime"}]
        filepath = save_raw_data(data)

        assert filepath.startswith(str(tmp_path))
        with open(filepath, encoding="utf-8") as f:
            saved = json.load(f)
        assert saved == data