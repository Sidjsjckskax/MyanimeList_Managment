from pathlib import Path
from datetime import datetime

import pandas as pd
from pydantic import ValidationError
from src.config import FINITO_DATA_PATH
from src.logger import setup_logger
from src.schemas import AnimeClean

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

    if not raw_data:
        logger.warning("Nessun dato grezzo da trasformare")
        return pd.DataFrame()

    cleaned = [_clean_record(r) for r in raw_data]
    df = pd.DataFrame(cleaned)

    before = len(df)
    df = df.dropna(subset=["mal_id"])
    df["mal_id"] = df["mal_id"].astype(int)
    df = df.drop_duplicates(subset=["mal_id"])
    logger.info(f"Rimossi {before - len(df)} record senza mal_id o duplicati")

    for col in ("aired_from", "aired_to"):
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    int_columns = ["episodes", "rank_", "popularity", "members", "favorites", "scored_by", "year_"]
    for col in int_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df = df.astype(object).where(df.notna(), None)

    df = _validate_records(df)

    logger.info(f"Trasformazione completata: {len(df)} record puliti")
    return df


def _validate_records(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    validi = []
    scartati = 0

    for record in df.to_dict(orient="records"):
        try:
            validato = AnimeClean(**record)
            validi.append(validato.model_dump())
        except ValidationError as e:
            scartati += 1
            logger.warning(
                f"Record scartato (mal_id={record.get('mal_id')}, "
                f"title={record.get('title')!r}): {e.errors()[0]['msg']}"
            )

    if scartati:
        logger.warning(f"Validazione: {scartati} record scartati su {len(df)}")

    return pd.DataFrame(validi)


def save_finito_data(df: pd.DataFrame) -> str:
    """Salva i dati puliti (post-trasformazione) in formato CSV"""
    Path(FINITO_DATA_PATH).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{FINITO_DATA_PATH}/anime_finito_{timestamp}.csv"

    df.to_csv(filepath, index=False, encoding="utf-8")

    logger.info(f"Dati puliti salvati: {filepath} ({len(df)} record)")
    return filepath