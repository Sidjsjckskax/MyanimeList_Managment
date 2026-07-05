import os
from dotenv import load_dotenv
import os
from dotenv import load_dotenv

load_dotenv()

# jikan API
JIKAN_BASE_URL = "https://api.jikan.moe/v4"
JIKAN_RATE_LIMIT_DELAY = 1.2

# Database connection string
DATABASE_URL = os.getenv("DATABASE_URL")

# Paths
RAW_DATA_PATH = "data/raw"
FINITO_DATA_PATH = "data/finito"
MONITORING_LOG_PATH = "logs/monitoring.csv"

MAX_PAGES = 10

