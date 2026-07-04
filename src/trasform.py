import pandas as pd
from src.logger import setup_logger

logger = setup_logger(__name__)


def _join_names(items: list) -> str:
    """Trasforma una lista di dict {'name': ...} in stringa 'a, b, c'"""
    if not items:
        return None
    return ", ".join(i.get("name", "") for i in items if i.get("name"))


def _clean_record(raw: dict) -> dict:
    """Estrae e appiattisce i campi utili da un record Jikan grezzo"""
    aired = raw.get("aired") or {}

    return {
        "mal_id": raw.get("mal_id"),
        "title": raw.get("title"),
        "title_english": raw.get("title_english"),
        "title_japanese": raw.get("title_japanese"),
        "type_": raw.get("type"),
        "source_": raw.get("source"),
        "episodes": raw.get("episodes"),
        "status_": raw.get("status"),
        "airing": raw.get("airing"),
        "aired_from": aired.get("from"),
        "aired_to": aired.get("to"),
        "duration": raw.get("duration"),
        "rating": raw.get("rating"),
        "score": raw.get("score"),
        "scored_by": raw.get("scored_by"),
        "rank_": raw.get("rank"),
        "popularity": raw.get("popularity"),
        "members": raw.get("members"),
        "favorites": raw.get("favorites"),
        "synopsis": raw.get("synopsis"),
        "year_": raw.get("year"),
        "season": raw.get("season"),
        "studios": _join_names(raw.get("studios")),
        "genres": _join_names(raw.get("genres")),
        "themes": _join_names(raw.get("themes")),
        "demographics": _join_names(raw.get("demographics")),
    }


def transform_anime_data(raw_data: list[dict]) -> pd.DataFrame:
    """Pulisce e trasforma i dati grezzi di Jikan in un DataFrame pronto per il DB"""
    logger.info(f"Trasformazione di {len(raw_data)} record grezzi")

    cleaned = [_clean_record(r) for r in raw_data]
    df = pd.DataFrame(cleaned)

    before = len(df)
    df = df.dropna(subset=["mal_id"])
    df["mal_id"] = df["mal_id"].astype(int)
    df = df.drop_duplicates(subset=["mal_id"])
    logger.info(f"Rimossi {before - len(df)} record senza mal_id o duplicati")

    for col in ("aired_from", "aired_to"):
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    df = df.where(pd.notnull(df), None)

    logger.info(f"Trasformazione completata: {len(df)} record puliti")
    return df