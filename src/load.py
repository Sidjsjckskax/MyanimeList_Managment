import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from src.config import DATABASE_URL
from src.logger import setup_logger

logger = setup_logger(__name__)


def get_engine():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL non impostata nel .env")
    logger.info("Connessione al database...")
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},  # niente attesa infinita: fallisce dopo 10s
    )


def load_to_database(df: pd.DataFrame, table_name: str = "anime", if_exists: str = "append"):
    """Carica dati nel database (modalità append di default, non replace!)"""

    if df.empty:
        logger.warning("DataFrame vuoto, niente da caricare")
        return

    engine = get_engine()

    try:
        logger.info(f"Caricamento {len(df)} record in '{table_name}' (modalità: {if_exists})")
        df.to_sql(
            table_name,
            engine,
            if_exists=if_exists,
            index=False,
            chunksize=500,
            method="multi"
        )
        logger.info(f"Caricamento completato: {len(df)} record")

    except SQLAlchemyError as e:
        logger.error(f"Errore durante il caricamento: {e}", exc_info=True)
        raise

    finally:
        engine.dispose()


def upsert_to_database(df: pd.DataFrame, table_name: str = "anime", key_column: str = "mal_id"):
    """Upsert (insert or update) dei dati"""

    if df.empty:
        logger.warning("DataFrame vuoto, niente da fare")
        return

    if key_column not in df.columns:
        raise ValueError(f"Colonna '{key_column}' non trovata nel DataFrame")

    engine = get_engine()

    try:
        logger.info(f"Upsert {len(df)} record in '{table_name}' (chiave: {key_column})")

        with engine.begin() as conn:
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                columns = ", ".join(row_dict.keys())
                placeholders = ", ".join(f":{col}" for col in row_dict.keys())
                update_clause = ", ".join(
                    f"{col} = EXCLUDED.{col}" for col in row_dict.keys() if col != key_column
                )

                query = text(f"""
                    INSERT INTO {table_name} ({columns})
                    VALUES ({placeholders})
                    ON CONFLICT ({key_column})
                    DO UPDATE SET {update_clause}
                """)
                conn.execute(query, row_dict)

                if (idx + 1) % 100 == 0:
                    logger.debug(f"Processati {idx + 1}/{len(df)} record")

        logger.info(f"Upsert completato: {len(df)} record")

    except SQLAlchemyError as e:
        logger.error(f"Errore durante upsert: {e}", exc_info=True)
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        logger.info("Connessione al DB OK")