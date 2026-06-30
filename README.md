# MyanimeList
Pipeline per ETL per l'estrazione, trasformazionee caricamento dei dati anime dalla JikanAPI, con caricamento su database PostreSQL(Supabase) e visualizzazione tramite dashboard Power BI.

## Architettura
Jikan APIv4<--->Extract/Transform/Load(Python)<--->Supabase(PostreSQL)<--->PowerBI

Le pipeline vengono eseguite automaticvamente ogni settimana tramite GitHub Actions.

## Struttura del progetto

## Setup del Progetto

### 1. Clonar il repository
git clone 
cd MyanimeList_Managment

### 2. Installlare le dipendenze
pip install -r requirements

### 3. Cofigurare le variabili d'ambiente
copiare .env.example e configurare .env e inserire la connection string
usare la connection string pooler  non quella diretta

### 4. Avviare la pipeline 
python -m main.py

## Funzionalità principali
1 Estrazione dati anime da Jikan API v4



