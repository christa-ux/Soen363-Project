CREATE VIEW FullAccessSongs AS
SELECT 
    song_id,
    title,
    artist_id,
    chart_rank
FROM Songs;

CREATE VIEW RestrictedAccessSongs AS
SELECT 
    title,
    chart_rank
FROM Songs
WHERE chart_rank <= 50;
