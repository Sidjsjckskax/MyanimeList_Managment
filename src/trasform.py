from data.raw import csv
import math

PATH_CSV = 'anime.csv' 

def analizza_e_pulisci_anime(percorso_file):
    try:
        with open(percorso_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            num_colonne = len(headers)
            
            righe_grezze = []
            for riga in reader:
                if riga:
                    if len(riga) < num_colonne:
                        riga += [''] * (num_colonne - len(riga))
                    riga = riga[:num_colonne]
                    righe_grezze.append(riga)
            
            total_grezze = len(righe_grezze)
            if total_grezze == 0:
                print("Il dataset e vuoto!")
                return

            print("=" * 60)
            print("Domanda 2: ANALISI DELLA STRUTTURA DEI DATI")
            print("=" * 60)
            
            print(f"Attributi disponibili ({num_colonne}):\n{', '.join(headers)}\n")
            
            try:
                idx_id = headers.index('mal_id')
                idx_title = headers.index('title')
                idx_type = headers.index('type_')
                idx_episodes = headers.index('episodes')
                idx_score = headers.index('score')
                idx_members = headers.index('members')
                idx_genres = headers.index('genres')
            except ValueError as e:
                print(f"Errore: Campo non trovato nel CSV. Dettaglio: {e}")
                return

            print(f"{'Campo':<16} | {'Tipo Presunto':<15} | {'Mancanti':<12}")
            print("-" * 50)
            
            valori_mancanti = [0] * num_colonne
            for i in range(num_colonne):
                for riga in righe_grezze:
                    val_pulito = riga[i].strip().lower()
                    if val_pulito in ['', 'nan', 'null', 'none', 'unknown']:
                        valori_mancanti[i] += 1
                
                tipo_schema = "Testo"
                if headers[i] in ['mal_id', 'episodes', 'scored_by', 'rank_', 'popularity', 'members', 'favorites', 'year_']:
                    tipo_schema = "Intero"
                elif headers[i] == 'score':
                    tipo_schema = "Decimale (Numeric)"
                elif headers[i] == 'airing':
                    tipo_schema = "Booleano"
                elif headers[i] in ['aired_from', 'aired_to']:
                    tipo_schema = "Data"

                print(f"{headers[i][:16]:<16} | {tipo_schema:<15} | {valori_mancanti[i]} ({valori_mancanti[i]/total_grezze*100:.1f}%)")
            
            id_visti_check = set()
            duplicati_id = 0
            for r in righe_grezze:
                m_id = r[idx_id].strip()
                if m_id in id_visti_check:
                    duplicati_id += 1
                else:
                    id_visti_check.add(m_id)
                    
            print(f"\nDati duplicati (stesso mal_id): {duplicati_id} su {total_grezze}")
            
            print("\nCampi suggeriti per analisi interessanti:")
            print("  - 'score' vs 'members' (Voto medio legato alla popolarita)")
            print("  - 'type_' e 'genres' (Generi e formati piu diffusi)")

            print("\n" + "=" * 60)
            print("TRASFORMAZIONI E PULIZIA DATI (Effettuate 3 operazioni)")
            print("=" * 60)
            
            # OPERAZIONE 1: Eliminazione dei duplicati basata su 'mal_id'
            id_unici = set()
            righe_pulite = []
            for r in righe_grezze:
                m_id = r[idx_id].strip()
                if m_id not in id_unici:
                    id_unici.add(m_id)
                    righe_pulite.append(r)
            print(f"[1/3] Rimozione Duplicati: Filtrati da {total_grezze} a {len(righe_pulite)}")
            
            # OPERAZIONE 2: Gestione dei valori nulli e conversione tipi per 'score' ed 'episodes'
            for r in righe_pulite:
                val_score = r[idx_score].strip().replace(',', '.')
                try:
                    r[idx_score] = float(val_score)
                except ValueError:
                    r[idx_score] = 0.0
                
                val_ep = r[idx_episodes].strip()
                try:
                    r[idx_episodes] = int(val_ep)
                except ValueError:
                    r[idx_episodes] = 1
            print("[2/3] Gestione Nulli e Tipi: Convertiti 'score' in Decimale e 'episodes' in Intero")

            # OPERAZIONE 3: Creazione di un nuovo attributo derivato ('classe_durata')
            headers.append("classe_durata")
            for r in righe_pulite:
                num_ep = r[idx_episodes]
                tipo_anime = r[idx_type].strip().lower()
                
                if 'movie' in tipo_anime:
                    classe = "Film Singolo"
                elif num_ep == 1:
                    classe = "Special/OVA (1 ep)"
                elif 2 <= num_ep <= 13:
                    classe = "Serie Corta (1 Cour)"
                elif 14 <= num_ep <= 26:
                    classe = "Serie Standard (2 Cour)"
                else:
                    classe = "Serie Lunga (>26 ep)"
                r.append(classe)
            print("[3/3] Nuovo Attributo Derivato: Creata la colonna 'classe_durata'")

            print("\n" + "=" * 60)
            print("EDA")
            print("=" * 60)
            
            # 1. Statistiche descrittive di SCORE
            voti_validi = [r[idx_score] for r in righe_pulite if r[idx_score] > 0]
            if voti_validi:
                voti_ordinati = sorted(voti_validi)
                n_voti = len(voti_ordinati)
                media_score = sum(voti_ordinati) / n_voti
                mediana_score = voti_ordinati[n_voti // 2] if n_voti % 2 != 0 else (voti_ordinati[(n_voti//2)-1] + voti_ordinati[n_voti//2])/2
                
                var_score = sum((x - media_score) ** 2 for x in voti_ordinati) / n_voti
                std_score = math.sqrt(var_score)
                
                print("STATISTICHE DESCRITTIVE (Variabile: score):")
                print(f"  Anime Recensiti:     {n_voti}")
                print(f"  Punteggio Minimo:    {voti_ordinati[0]:.2f} | Punteggio Massimo: {voti_ordinati[-1]:.2f}")
                print(f"  Media Globale MAL:   {media_score:.2f} | Mediana:           {mediana_score:.2f}")
                print(f"  Deviazione Standard: {std_score:.2f}\n")

            # 2. Conteggi per Categoria ('classe_durata')
            print("CONTEGGI PER CATEGORIA (Nuovo attributo 'classe_durata'):")
            conteggio_durata = {}
            for r in righe_pulite:
                cat = r[-1]
                conteggio_durata[cat] = conteggio_durata.get(cat, 0) + 1
            
            for cat, count in sorted(conteggio_durata.items(), key=lambda x: x[1], reverse=True):
                pct = (count / len(righe_pulite)) * 100
                print(f"  - {cat:<25}: {count:<5} anime ({pct:.1f}%)")
                
            # 3. Conteggi per Categoria ('type_')
            print("\nDISTRIBUZIONE DELLA VARIABILE DI TIPOLOGIA ('type_'):")
            conteggio_type = {}
            for r in righe_pulite:
                t = r[idx_type].strip()
                if t == '': t = 'Non Specificato'
                conteggio_type[t] = conteggio_type.get(t, 0) + 1
            
            for t, count in sorted(conteggio_type.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {t:<12}: {count} record")

            print("\nScript terminato.")

    except FileNotFoundError:
        print(f"Errore: Impossibile trovare il file '{percorso_file}'.")
    except Exception as e:
        print(f"Errore imprevisto: {e}")

analizza_e_pulisci_anime(PATH_CSV)