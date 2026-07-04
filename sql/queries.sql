-- Conteggio totale anime nel database
SELECT COUNT(*) AS totale_anime FROM anime;

-- Controllo duplicati (non dovrebbero essercene, usando upsert)
SELECT mal_id, COUNT(*) AS occorrenze
FROM anime
GROUP BY mal_id
HAVING COUNT(*) > 1;

-- Top 10 anime per punteggio (con almeno 1000 voti, per evitare outlier)
SELECT title, score, scored_by, members
FROM anime
WHERE scored_by >= 1000
ORDER BY score DESC NULLS LAST
LIMIT 10;

-- Top 10 anime per popolarità (membri)
SELECT title, members, score
FROM anime
ORDER BY members DESC NULLS LAST
LIMIT 10;

-- Distribuzione anime per anno di uscita
SELECT year_, COUNT(*) AS numero_anime
FROM anime
WHERE year_ IS NOT NULL
GROUP BY year_
ORDER BY year_ DESC;

-- Distribuzione anime per stagione (spring/summer/fall/winter)
SELECT year_, season, COUNT(*) AS numero_anime
FROM anime
WHERE year_ IS NOT NULL AND season IS NOT NULL
GROUP BY year_, season
ORDER BY year_ DESC, season;

-- Anime per tipo (TV, Movie, OVA, ecc.)
SELECT type_, COUNT(*) AS numero_anime
FROM anime
GROUP BY type_
ORDER BY numero_anime DESC;

-- Anime per stato (Airing, Finished Airing, Not yet aired)
SELECT status_, COUNT(*) AS numero_anime
FROM anime
GROUP BY status_
ORDER BY numero_anime DESC;

-- Genere più frequente (richiede che "genres" sia una stringa "a, b, c")
SELECT TRIM(genere) AS genere, COUNT(*) AS numero_anime
FROM anime, LATERAL unnest(string_to_array(genres, ', ')) AS genere
WHERE genres IS NOT NULL
GROUP BY TRIM(genere)
ORDER BY numero_anime DESC;

SELECT TRIM(studio) AS studio, COUNT(*) AS numero_anime
FROM anime, LATERAL unnest(string_to_array(studios, ', ')) AS studio
WHERE studios IS NOT NULL
GROUP BY TRIM(studio)
ORDER BY numero_anime DESC
LIMIT 15;

-- Anime che stanno ora
SELECT title, episodes, aired_from, studios
FROM anime
WHERE airing = TRUE
ORDER BY aired_from DESC;

-- Anime senza sinossi
SELECT mal_id, title
FROM anime
WHERE synopsis IS NULL OR synopsis = '';