import time
import json
import requests
from pathlib import Path
from datetime import datetime

from src.config import JIKAN_BASE_URL, JIKAN_RATE_LIMIT_DELAY, RAW_DATA_PATH, MAX_PAGES


def fetch_anime_page(page: int) -> dict:
    url = f"{JIKAN_BASE_URL}/anime"
    params = {"page": page, "limit": 25}

    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 429:
        print(f"Rate limit raggiunto a pagina {page}, attendo 5s...")
        time.sleep(5)
        return fetch_anime_page(page)

    response.raise_for_status()
    return response.json()


def extract_all_anime(max_pages: int = MAX_PAGES) -> list[dict]:
    all_anime = []

    for page in range(1, max_pages + 1):
        try:
            data = fetch_anime_page(page)
        except requests.exceptions.RequestException as e:
            print(f"Errore alla pagina {page}: {e}")
            break

        records = data.get("data", [])
        if not records:
            print(f"Nessun dato alla pagina {page}, fine estrazione.")
            break

        all_anime.extend(records)
        print(f"Pagina {page}/{max_pages} estratta ({len(records)} record, totale: {len(all_anime)})")

        has_next = data.get("pagination", {}).get("has_next_page", False)
        if not has_next:
            print("Raggiunta ultima pagina disponibile.")
            break

        time.sleep(JIKAN_RATE_LIMIT_DELAY)

    return all_anime


def save_raw_data(data: list[dict]) -> str:
    Path(RAW_DATA_PATH).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{RAW_DATA_PATH}/anime_raw_{timestamp}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Dati grezzi salvati in {filepath} ({len(data)} record)")
    return filepath


if __name__ == "__main__":
    anime_data = extract_all_anime()
    save_raw_data(anime_data)

