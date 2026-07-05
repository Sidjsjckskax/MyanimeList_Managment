from src.jikan import extract_all_anime, save_raw_data
from src.trasform import transform_anime_data, save_finito_data
from src.load import upsert_to_database
from src.logger import setup_logger
from src.monitoring import PipelineRunMonitor

logger = setup_logger(__name__)


def run_pipeline():
    monitor = PipelineRunMonitor()

    try:
        logger.info("=" * 50)
        logger.info("INIZIO PIPELINE ETL")
        logger.info("=" * 50)

        # EXTRACT
        logger.info("\n[1/3] EXTRACT")
        try:
            raw_data = extract_all_anime()
            filepath = save_raw_data(raw_data)
            monitor.set_estratti(len(raw_data))
            logger.info(f"Extract completato: {len(raw_data)} record")
        except Exception as e:
            logger.error(f"Extract fallito: {e}", exc_info=True)
            raise

        # TRANSFORM
        logger.info("\n[2/3] TRANSFORM")
        try:
            df_clean = transform_anime_data(raw_data)
            save_finito_data(df_clean)
            monitor.set_trasformati(len(df_clean))
            logger.info(f"Transform completato: {len(df_clean)} record")
        except Exception as e:
            logger.error(f"Transform fallito: {e}", exc_info=True)
            raise

        # LOAD
        logger.info("\n[3/3] LOAD")
        try:
            upsert_to_database(df_clean)
            monitor.set_caricati(len(df_clean))
            logger.info("Load completato")
        except Exception as e:
            logger.error(f"Load fallito: {e}", exc_info=True)
            raise

        logger.info("\n" + "=" * 50)
        logger.info("PIPELINE COMPLETATA CON SUCCESSO")
        logger.info("=" * 50)
        monitor.salva_successo()

    except Exception as e:
        logger.critical(f"PIPELINE FALLITA: {e}", exc_info=True)
        monitor.salva_fallimento(e)
        raise


if __name__ == "__main__":
    run_pipeline()