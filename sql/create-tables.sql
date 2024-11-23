CREATE TABLE Artists (
    artist_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image_url VARCHAR(255),
    spotify_url VARCHAR(255),
    type VARCHAR(50) NOT NULL CHECK (type IN ('MusicianArtist', 'AudiobookArtist'))
);


CREATE TABLE AudiobookArtists (
    artist_id BIGINT UNSIGNED PRIMARY KEY,
    biography TEXT,
    total_books INT,
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);


CREATE TABLE MusicianArtists (
    artist_id BIGINT UNSIGNED PRIMARY KEY,
    popularity INT,
    followers INT,
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);


CREATE TABLE Audiobooks (
    audiobook_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    total_chapters INT,
    artist_id BIGINT UNSIGNED,
    FOREIGN KEY (artist_id) REFERENCES AudiobookArtists(artist_id)
);

CREATE TABLE Chapters (
    chapter_id BIGINT UNSIGNED AUTO_INCREMENT,
    audiobook_id BIGINT UNSIGNED REFERENCES Audiobooks(audiobook_id) ON DELETE CASCADE,
    chapter_number INT NOT NULL,
    duration_ms INT,
    audio_preview_url VARCHAR(255),
    release_date DATE,
    PRIMARY KEY (chapter_id, audiobook_id),
    FOREIGN KEY (audiobook_id) REFERENCES Audiobooks(audiobook_id)
);

CREATE TABLE Audiobook_Owns (
    audiobook_id BIGINT UNSIGNED,
    artist_id BIGINT UNSIGNED,
    PRIMARY KEY (audiobook_id, artist_id),
    FOREIGN KEY (audiobook_id) REFERENCES Audiobooks(audiobook_id),
    FOREIGN KEY (artist_id) REFERENCES AudiobookArtists(artist_id)
);

CREATE TABLE Countries (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL
);

INSERT INTO Countries (country_name) VALUES 
    ('United States'),
    ('United Kingdom'),
    ('Belgium'),
    ('France'),
    ('Canada');

CREATE TABLE Songs (
    song_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist_id BIGINT UNSIGNED,
    chart_rank INT,
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);