import pandas as pd

from src.trasform import transform_anime_data, save_finito_data, _clean_record, _join_names


RAW_SAMPLE = {
    "mal_id": 1,
    "title": "Cowboy Bebop",
    "title_english": "Cowboy Bebop",
    "title_japanese": "カウボーイビバップ",
    "type": "TV",
    "source": "Original",
    "episodes": 26,
    "status": "Finished Airing",
    "airing": False,
    "aired": {"from": "1998-04-03T00:00:00+00:00", "to": "1999-04-24T00:00:00+00:00"},
    "duration": "24 min per ep",
    "rating": "R - 17+",
    "score": 8.75,
    "scored_by": 900000,
    "rank": 40,
    "popularity": 39,
    "members": 1800000,
    "favorites": 80000,
    "synopsis": "In un futuro...",
    "year": 1998,
    "season": "spring",
    "studios": [{"name": "Sunrise"}],
    "genres": [{"name": "Action"}, {"name": "Adventure"}],
    "themes": [{"name": "Space"}],
    "demographics": [],
}


class TestJoinNames:

    def test_lista_vuota_ritorna_none(self):
        assert _join_names([]) is None

    def test_none_ritorna_none(self):
        assert _join_names(None) is None

    def test_unisce_piu_nomi(self):
        assert _join_names([{"name": "Action"}, {"name": "Comedy"}]) == "Action, Comedy"


class TestCleanRecord:

    def test_estrae_tutti_i_campi_principali(self):
        cleaned = _clean_record(RAW_SAMPLE)
        assert cleaned["mal_id"] == 1
        assert cleaned["title"] == "Cowboy Bebop"
        assert cleaned["type_"] == "TV"
        assert cleaned["source_"] == "Original"
        assert cleaned["aired_from"] == "1998-04-03T00:00:00+00:00"
        assert cleaned["studios"] == "Sunrise"
        assert cleaned["genres"] == "Action, Adventure"
        assert cleaned["demographics"] is None

    def test_gestisce_aired_mancante(self):
        raw = dict(RAW_SAMPLE)
        raw.pop("aired")
        cleaned = _clean_record(raw)
        assert cleaned["aired_from"] is None
        assert cleaned["aired_to"] is None


class TestTransformAnimeData:

    def test_ritorna_dataframe_con_colonne_attese(self):
        df = transform_anime_data([RAW_SAMPLE])
        assert isinstance(df, pd.DataFrame)
        assert "mal_id" in df.columns
        assert "score" in df.columns
        assert len(df) == 1

    def test_rimuove_record_senza_mal_id(self):
        raw_senza_id = dict(RAW_SAMPLE)
        raw_senza_id["mal_id"] = None
        df = transform_anime_data([RAW_SAMPLE, raw_senza_id])
        assert len(df) == 1

    def test_rimuove_duplicati_per_mal_id(self):
        df = transform_anime_data([RAW_SAMPLE, RAW_SAMPLE])
        assert len(df) == 1

    def test_converte_date_correttamente(self):
        df = transform_anime_data([RAW_SAMPLE])
        assert str(df.iloc[0]["aired_from"]) == "1998-04-03"

    def test_lista_vuota_ritorna_dataframe_vuoto(self):
        df = transform_anime_data([])
        assert df.empty


class TestValidazionePydantic:

    def test_scarta_record_con_score_impossibile(self):
        raw_rotto = dict(RAW_SAMPLE, mal_id=2, title="Anime Rotto", score=999.0)
        df = transform_anime_data([RAW_SAMPLE, raw_rotto])
        assert len(df) == 1
        assert df.iloc[0]["mal_id"] == 1

    def test_scarta_record_senza_titolo(self):
        raw_senza_titolo = dict(RAW_SAMPLE, mal_id=3, title="")
        df = transform_anime_data([RAW_SAMPLE, raw_senza_titolo])
        assert len(df) == 1

    def test_tiene_record_con_campi_opzionali_mancanti(self):
        raw_minimo = dict(RAW_SAMPLE, mal_id=4, title="Anime Minimo", score=None, year=None, season=None)
        df = transform_anime_data([raw_minimo])
        assert len(df) == 1


class TestSaveFinitoData:

    def test_salva_csv_e_ritorna_path(self, tmp_path, monkeypatch):
        import src.trasform as trasform_module
        monkeypatch.setattr(trasform_module, "FINITO_DATA_PATH", str(tmp_path))

        df = transform_anime_data([RAW_SAMPLE])
        filepath = save_finito_data(df)

        assert filepath.endswith(".csv")
        assert filepath.startswith(str(tmp_path))

        df_riletto = pd.read_csv(filepath)
        assert df_riletto.iloc[0]["mal_id"] == 1
        assert df_riletto.iloc[0]["title"] == "Cowboy Bebop"