from src.jikan import extract_all_anime, save_raw_data
from src.trasform import transform_anime_data
from src.load import load_to_database


def run_pipeline():
    print("=== AVVIO PIPELINE ETL ===")

    print("\n[1/3] EXTRACT")
    raw_data = extract_all_anime()
    save_raw_data(raw_data)

    print("\n[2/3] TRANSFORM")
    df_clean = transform_anime_data(raw_data)

    print("\n[3/3] LOAD")
    load_to_database(df_clean)

    print("\n=== PIPELINE COMPLETATA ===")


if __name__ == "__main__":
    run_pipeline()