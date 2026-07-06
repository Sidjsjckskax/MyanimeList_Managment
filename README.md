# MyanimeList Management

Pipeline ETL per l'estrazione, la trasformazione e il caricamento dei dati anime dalla Jikan API, con caricamento su database PostgreSQL (Supabase) e visualizzazione tramite dashboard Power BI.

## Architettura

```
Jikan API v4  <--->  Extract / Transform / Load (Python)  <--->  Supabase (PostgreSQL)  <--->  Power BI
```

La pipeline viene eseguita automaticamente ogni settimana (ogni lunedì alle 6:00 UTC) tramite GitHub Actions, e può anche essere lanciata manualmente.

## Struttura del progetto

```
MyanimeList_Managment/
├── main.py                    # Entry point della pipeline
├── conftest.py                # Configurazione pytest (rende importabile src/ nei test)
├── requirements.txt
├── src/
│   ├── config.py               # Variabili di configurazione (path, URL, limiti)
│   ├── jikan.py                 # Fase EXTRACT: chiamate all'API Jikan con retry
│   ├── trasform.py              # Fase TRANSFORM: pulizia e normalizzazione dati
│   ├── load.py                  # Fase LOAD: upsert su Supabase
│   ├── logger.py                 # Configurazione logging su file e console
│   ├── monitoring.py             # Riepilogo strutturato di ogni esecuzione
│   └── pipeline.py               # Orchestrazione Extract -> Transform -> Load
├── test/                       # Test unitari (pytest, con mock: nessuna chiamata reale ad API/DB)
├── sql/
│   ├── schema.sql               # Definizione tabella anime
│   └── queries.sql              # Query di analisi pronte all'uso
├── notebooks/
│   └── eda.ipynb                # Analisi esplorativa sui dati più recenti (legge da data/finito)
├── data/
│   ├── raw/                     # Dati grezzi da Jikan (CSV, non tracciati in git)
│   └── finito/                  # Dati puliti pronti per il DB (CSV, non tracciati in git)
├── logs/
│   ├── pipeline_*.log            # Log dettagliati per ogni esecuzione
│   └── monitoring.csv            # Riepilogo di tutte le esecuzioni (una riga per run)
├── powerbi/
│   └── dashboard.pbix            # Dashboard Power BI
└── .github/workflows/pipeline.yml # Esecuzione automatica settimanale
```

## Setup del progetto

### 1. Clonare il repository
```
git clone https://github.com/<tuo-utente>/MyanimeList_Managment.git
cd MyanimeList_Managment
```

### 2. Installare le dipendenze
```
pip install -r requirements.txt
```

### 3. Configurare le variabili d'ambiente
Copiare `.env.example` in `.env` e inserire la connection string del database:
```
cp .env.example .env
```
Usare la connection string **pooler** di Supabase (porta `6543`), non quella diretta, per evitare problemi di risoluzione DNS/IPv6.

### 4. Avviare la pipeline
```
python main.py
```

## Testing

I test non fanno mai chiamate reali all'API Jikan né al database (tutto viene simulato con `unittest.mock`), quindi si possono eseguire offline in pochi secondi:
```
pytest test/ -v
```

## Monitoraggio

Ogni esecuzione della pipeline registra un riepilogo in `logs/monitoring.csv`: data/ora di inizio e fine, numero di record estratti/trasformati/caricati, stato (`SUCCESSO`/`FALLITO`) ed eventuale messaggio di errore. È pensato per essere aperto direttamente in Excel o letto con `pandas.read_csv()`.

Per il dettaglio riga per riga di una singola esecuzione, consultare il file corrispondente in `logs/pipeline_<timestamp>.log`.

## Analisi esplorativa (EDA)

Il notebook `notebooks/eda.ipynb` legge automaticamente il file più recente in `data/finito/` e produce grafici su distribuzione degli score, generi e studi più frequenti, anime per anno/stagione, e altro. Va rieseguito dopo ogni run della pipeline per aggiornare i dati.

## Funzionalità principali

1. Estrazione dati anime da Jikan API v4, con retry automatico su rate limit (429) ed errori temporanei del server (5xx)
2. Trasformazione e pulizia dei dati (rimozione duplicati, gestione valori mancanti, normalizzazione date)
3. Caricamento su Supabase con upsert (aggiorna i record esistenti invece di duplicarli)
4. Salvataggio dei dati grezzi e puliti in formato CSV (`data/raw/`, `data/finito/`)
5. Monitoraggio strutturato di ogni esecuzione (`logs/monitoring.csv`)
6. Test automatizzati (`pytest`), eseguiti anche automaticamente prima di ogni run pianificato su GitHub Actions
7. Dashboard Power BI ed EDA in notebook Jupyter



