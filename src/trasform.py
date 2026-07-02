import re
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"Inizio trasformazione: {len(df)} record")
    
    df = rimuovi_duplicati(df)
    df = gestisci_null(df)
    df = converti_tipi(df)
    df = aggiungi_score_tier(df)
    df = aggiungi_classe_durata(df)
    
    logger.info(f"Trasformazione completata: {len(df)} record")
    return df


def rimuovi_duplicati(df: pd.DataFrame) -> pd.DataFrame:
    prima = len(df)
    df = df.drop_duplicates(subset=["mal_id"], keep="first")
    rimossi = prima - len(df)
    if rimossi > 0:
        logger.info(f"Duplicati rimossi: {rimossi}")
    return df


def gestisci_null(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["score", "rank", "popularity", "members", "episodes", "year"]:
        if col in df.columns:
            n = df[col].isnull().sum()
            df[col] = df[col].fillna(0)
            if n > 0:
                logger.info(f"'{col}': {n} null → 0")
    
    for col in ["title", "synopsis", "genres", "studios", "themes", "rating", "source", "duration", "season", "type", "status"]:
        if col in df.columns:
            df[col] = df[col].fillna("")
    
    return df


def converti_tipi(df: pd.DataFrame) -> pd.DataFrame:
    int_cols = ["mal_id", "episodes", "rank", "popularity", "members", "year"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    
    float_cols = ["score"]
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)
    
    return df


def aggiungi_score_tier(df: pd.DataFrame) -> pd.DataFrame:
    def classifica(score):
        if score >= 8.5:
            return "Masterpiece"
        elif score >= 7.5:
            return "Great"
        elif score >= 6.0:
            return "Good"
        elif score > 0:
            return "Average"
        else:
            return "Unrated"
    
    df["score_tier"] = df["score"].apply(classifica)
    logger.info("score_tier creato")
    return df


def aggiungi_classe_durata(df: pd.DataFrame) -> pd.DataFrame:
    def calcola_classe(row):
        tipo = str(row.get("type", "")).strip().lower()
        ep = int(row.get("episodes", 0))
        
        if "movie" in tipo:
            return "Film Singolo"
        elif ep == 1:
            return "Special/OVA"
        elif 2 <= ep <= 13:
            return "Serie Corta"
        elif 14 <= ep <= 26:
            return "Serie Standard"
        else:
            return "Serie Lunga"
    
    df["classe_durata"] = df.apply(calcola_classe, axis=1)
    logger.info("classe_durata creato")
    return df


if __name__ == "__main__":
    df_test = pd.DataFrame([
        {"mal_id": 1, "title": "Test", "score": 8.5, "episodes": 12, "type": "TV"}
    ])
    df_clean = transform(df_test)
    print(df_clean)