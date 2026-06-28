import os
from dotenv import load_dotenv

load_dotenv()

# jikan API
JIKAN_BASE_URL = "https://api.jikan.moe/v4"
jIKAN_RATE_LIMIT_DELAY = 1.2

# Supabase per PostreSQL
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Paths
RAW_DATA_PATH = "data/raw"
FINITO_DATA_PATH = "data/finito"

MAX_PAGES = 400

