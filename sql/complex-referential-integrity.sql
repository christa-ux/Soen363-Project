DELIMITER //

CREATE TRIGGER restrict_song_count
BEFORE INSERT ON Songs
FOR EACH ROW
BEGIN
    DECLARE song_count INT;

    -- Count the total number of songs for the artist
    SELECT COUNT(*)
    INTO song_count
    FROM Songs
    WHERE artist_id = NEW.artist_id;

    -- Check if the artist already has 10 songs
    IF song_count >= 10 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'An artist cannot have more than 10 songs.';
    END IF;
END;
//
DELIMITER ;


------------- this query will fail due to the trigger -------------

-- Insert an artist
INSERT INTO Artists (artist_id, name, type) VALUES (1234567891110, 'ArtistName', 'MusicianArtist');

-- Insert up to 100 songs for this artist
INSERT INTO Songs (title, artist_id, chart_rank)
VALUES ('Song 1', 1234567891110, 1), ('Song 2', 1234567891110, 2), ('Song 3', 1234567891110, 3), 
       ('Song 4', 1234567891110, 4), ('Song 5', 1234567891110, 5), ('Song 6', 1234567891110, 6),
       ('Song 7', 1234567891110, 7), ('Song 8', 1234567891110, 8), ('Song 9', 1234567891110, 9),
       ('Song 10', 1234567891110, 10), ('Song 11', 1234567891110, 11);
