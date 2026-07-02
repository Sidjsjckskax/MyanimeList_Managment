import time
import json
import requests
from pathlib import Path
from datetime import datetime
from config import JIKAN_BASE_URL, JIKAN_RATE_LIMIT_DELAY, RAW_DATA_PATH, MAX_PAGES
from logger import setup_logger

logger = setup_logger(__name__)

def fetch_with_retry(url: str, params: dict, max_retries: int = 3, timeout: int = 10) -> dict:
    """Fetch con retry logic (exponential backoff)"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            
            if response.status_code == 429:
                wait_time = (2 ** attempt) * 5  
                logger.warning(f"Rate limit raggiunto. Attesa {wait_time}s (tentativo {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout al tentativo {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep((2 ** attempt) * 2)
            continue
            
        except requests.exceptions.ConnectionError:
            logger.warning(f"Errore di connessione al tentativo {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep((2 ** attempt) * 2)
            continue
    
    raise requests.exceptions.RequestException(f"Fallito dopo {max_retries} tentativi")


def fetch_anime_page(page: int) -> dict:
    """Fetch singola pagina"""
    url = f"{JIKAN_BASE_URL}/anime"
    params = {"page": page, "limit": 25}
    return fetch_with_retry(url, params)


def extract_all_anime(max_pages: int = MAX_PAGES) -> list[dict]:
    """Estrai tutti gli anime"""
    all_anime = []
    logger.info(f"Inizio estrazione anime (max {max_pages} pagine)")

    for page in range(1, max_pages + 1):
        try:
            data = fetch_anime_page(page)
        except requests.exceptions.RequestException as e:
            logger.error(f"Errore pagina {page}: {e}. Estrazione fermata.")
            break

        records = data.get("data", [])
        if not records:
            logger.info(f"Nessun dato pagina {page}. Fine estrazione.")
            break

        all_anime.extend(records)
        logger.info(f"Pagina {page}/{max_pages}: {len(records)} record (totale: {len(all_anime)})")

        has_next = data.get("pagination", {}).get("has_next_page", False)
        if not has_next:
            logger.info("Raggiunta ultima pagina disponibile")
            break

        time.sleep(JIKAN_RATE_LIMIT_DELAY)

    logger.info(f"Estrazione completata: {len(all_anime)} record totali")
    return all_anime


def save_raw_data(data: list[dict]) -> str:
    """Salva dati grezzi"""
    Path(RAW_DATA_PATH).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{RAW_DATA_PATH}/anime_raw_{timestamp}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Dati grezzi salvati: {filepath} ({len(data)} record)")
    return filepath


if __name__ == "__main__":
    anime_data = extract_all_anime()
    save_raw_data(anime_data)
