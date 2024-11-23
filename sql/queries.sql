-------------------- Basic select with simple where clause --------------------
SELECT title, chart_rank 
FROM Songs 
WHERE artist_id = (SELECT artist_id FROM Artists WHERE name = 'Nirvana');




-------------------- Basic select with simple group by clause (with and without having clause) --------------------

-- Count the total number of songs per artist
SELECT a.name AS artist_name, COUNT(s.song_id) AS total_songs
FROM Songs s
JOIN Artists a ON s.artist_id = a.artist_id
GROUP BY a.name;

-- Count the total number of songs per artist, only show artists with more than 5 songs
SELECT a.name AS artist_name, COUNT(s.song_id) AS total_songs
FROM Songs s
JOIN Artists a ON s.artist_id = a.artist_id
GROUP BY a.name
HAVING total_songs > 5;



-------------------- A simple join query as well as its equivalent implementation using cartesian product and where clause --------------------

-- Retrieve all songs and their corresponding artist names using a JOIN
SELECT s.title, a.name AS artist_name
FROM Songs s
JOIN Artists a ON s.artist_id = a.artist_id;

-- Retrieve all songs and their corresponding artist names using a Cartesian product and WHERE clause
SELECT s.title, a.name AS artist_name
FROM Songs s, Artists a
WHERE s.artist_id = a.artist_id;




-------------------- A few queries to demonstrate various join types on the same tables: inner vs. outer --------------------
-------------------- (left and right) vs. full join. Use of null values in the database to show the differences is required --------------------

-- Inner Join: Retrieve all artists and their songs
SELECT a.name AS artist_name, s.title
FROM Artists a
JOIN Songs s ON a.artist_id = s.artist_id;

-- Left Outer Join: Retrieve all artists, including those without songs
SELECT a.name AS artist_name, s.title
FROM Artists a
LEFT JOIN Songs s ON a.artist_id = s.artist_id;

-- Right Outer Join: Retrieve all songs, including those without artists
SELECT a.name AS artist_name, s.title
FROM Artists a
RIGHT JOIN Songs s ON a.artist_id = s.artist_id;

-- Full Outer Join: Retrieve all artists and songs, even if they are not related
SELECT a.name AS artist_name, s.title
FROM Artists a
LEFT JOIN Songs s ON a.artist_id = s.artist_id
UNION
SELECT a.name AS artist_name, s.title
FROM Artists a
RIGHT JOIN Songs s ON a.artist_id = s.artist_id;




-------------------- A few queries to demonstrate use of Null values for undefined / non-applicable --------------------

-- Retrieve artists who do not have any songs
SELECT name 
FROM Artists 
WHERE artist_id NOT IN (SELECT artist_id FROM Songs);

-- Retrieve artists who do not have any songs using LEFT JOIN
SELECT a.name 
FROM Artists a
LEFT JOIN Songs s ON a.artist_id = s.artist_id
WHERE s.artist_id IS NULL;




-------------------- A couple of examples to demonstrate correlated queries --------------------

-- Find songs that rank higher than the average rank of all songs
SELECT title, chart_rank 
FROM Songs s1
WHERE chart_rank < (SELECT AVG(chart_rank) FROM Songs);

-- Find artists with more than 3 songs
SELECT name 
FROM Artists a
WHERE (SELECT COUNT(*) FROM Songs s WHERE s.artist_id = a.artist_id) > 3;




-------------------- One example per set operations: intersect, union, and difference vs. their equivalences --------------------
-------------------- without using set operations --------------------

-- Intersection: Find artists who have both songs and audiobooks
SELECT name 
FROM Artists a
WHERE EXISTS (SELECT 1 FROM Songs s WHERE s.artist_id = a.artist_id)
AND EXISTS (SELECT 1 FROM AudiobookArtists ab WHERE ab.artist_id = a.artist_id);

-- Union: Combine musician artists and audiobook artists
SELECT artist_id, name, 'MusicianArtist' AS type 
FROM Artists 
WHERE artist_id IN (SELECT artist_id FROM MusicianArtists)
UNION
SELECT artist_id, name, 'AudiobookArtist' AS type 
FROM Artists 
WHERE artist_id IN (SELECT artist_id FROM AudiobookArtists);

-- Difference: Find artists who are only musicians and not audiobook artists
SELECT artist_id, name 
FROM Artists 
WHERE artist_id IN (SELECT artist_id FROM MusicianArtists)
AND artist_id NOT IN (SELECT artist_id FROM AudiobookArtists);

--Intersect
-- Find artists who have both songs and audiobooks using JOINs
SELECT a.name
FROM Artists a
JOIN Songs s ON a.artist_id = s.artist_id
JOIN AudiobookArtists ab ON a.artist_id = ab.artist_id; 

--union
-- Combine musician artists and audiobook artists using JOIN and OR condition
SELECT a.artist_id, a.name, 
       CASE 
           WHEN a.artist_id IN (SELECT artist_id FROM MusicianArtists) THEN 'MusicianArtist'
           WHEN a.artist_id IN (SELECT artist_id FROM AudiobookArtists) THEN 'AudiobookArtist'
       END AS type
FROM Artists a
WHERE a.artist_id IN (SELECT artist_id FROM MusicianArtists)
OR a.artist_id IN (SELECT artist_id FROM AudiobookArtists);

-- Difference
-- Find artists who are only musicians and not audiobook artists using LEFT JOIN
SELECT a.artist_id, a.name 
FROM Artists a
JOIN MusicianArtists ma ON a.artist_id = ma.artist_id
LEFT JOIN AudiobookArtists ab ON a.artist_id = ab.artist_id
WHERE ab.artist_id IS NULL;




-------------------- An example of a view that has a hard-coded criteria, by which the content of the view --------------------
-------------------- may change upon changing the hard-coded value --------------------

CREATE VIEW TopChartSongs AS
SELECT 
    song_id,
    title,
    artist_id,
    chart_rank
FROM Songs
WHERE chart_rank <= 10; -- original hard-coded criteria

SELECT * FROM TopChartSongs;

CREATE OR REPLACE VIEW TopChartSongs AS
SELECT 
    song_id,
    title,
    artist_id,
    chart_rank
FROM Songs
WHERE chart_rank <= 20; -- new hard-coded criteria

SELECT * FROM TopChartSongs; --will return the new result set




-------------------- Two queries that demonstrate the overlap and covering constraints --------------------

-- overlap constraint that checks if any record in the Artists table appears in both AudiobookArtists and MusicianArtists
-- this query should return no rows because an artist cannot simultaneously be both an AudiobookArtist and a MusicianArtist (check ISA)
SELECT a.artist_id, a.name
FROM AudiobookArtists ab
JOIN MusicianArtists ma ON ab.artist_id = ma.artist_id
JOIN Artists a ON a.artist_id = ab.artist_id;

-- covering constraint that checks if every artist in the Artists table belongs to at least one of the subclasses (AudiobookArtists or MusicianArtists)
-- this query should return no rows because every artist must belong to at least one subclass (check ISA)
SELECT a.artist_id, a.name
FROM Artists a
LEFT JOIN AudiobookArtists ab ON a.artist_id = ab.artist_id
LEFT JOIN MusicianArtists ma ON a.artist_id = ma.artist_id
WHERE ab.artist_id IS NULL AND ma.artist_id IS NULL;



-------------------- Two implementations of the division operator using a) a regular nested query using --------------------
-------------------- NOT IN and b) a correlated nested query using NOT EXISTS and EXCEPT --------------------


-- 8. Division Operator Using NOT IN
-- Find artists who have songs in every country using NOT IN
SELECT a.name 
FROM Artists a
WHERE NOT EXISTS (
    SELECT c.country_id 
    FROM Countries c
    WHERE c.country_id NOT IN (
        SELECT s.chart_rank 
        FROM Songs s
        WHERE s.artist_id = a.artist_id
    )
);

-- Explanation:
-- 1. The inner query retrieves the countries where an artist has songs.
-- 2. The middle query checks for countries where the artist has no songs.
-- 3. The outer query retrieves only those artists for whom the middle query returns no rows,
--    meaning the artist has songs in all countries.


-- Division Operator Using NOT EXISTS
-- Find artists who have songs in every country using NOT EXISTS
SELECT a.name 
FROM Artists a
WHERE NOT EXISTS (
    SELECT * 
    FROM Countries c
    WHERE NOT EXISTS (
        SELECT * 
        FROM Songs s
        WHERE s.chart_rank = c.country_id AND s.artist_id = a.artist_id
    )
);

-- Explanation:
-- 1. The innermost query checks whether a specific artist has a song in a specific country.
-- 2. The middle query ensures that for every country, there is at least one corresponding song by the artist.
-- 3. The outer query retrieves only those artists for whom the middle query is false for no country.


-- Division Operator Using EXCEPT
-- Find artists who have songs in every country using EXCEPT (PostgreSQL/SQL Server only)
SELECT a.name 
FROM Artists a
WHERE NOT EXISTS (
    SELECT c.country_id 
    FROM Countries c
    EXCEPT
    SELECT s.chart_rank 
    FROM Songs s
    WHERE s.artist_id = a.artist_id
);

-- Explanation:
-- 1. The inner query (EXCEPT) retrieves countries where the artist does not have a song.
-- 2. The outer query ensures the artist is included only if there are no missing countries.
-- ** MySQL does not support EXCEPT