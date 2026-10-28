DROP DATABASE IF EXISTS event_registration;
CREATE DATABASE event_registration;
USE event_registration;

CREATE TABLE events (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    event_date DATE         NOT NULL,
    location   VARCHAR(100) NOT NULL,
    capacity   INT          NOT NULL CHECK (capacity > 0)
);

CREATE TABLE participants (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20)
);

CREATE TABLE registrations (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    event_id       INT NOT NULL,
    participant_id INT NOT NULL,
    registered_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id)       REFERENCES events(id)       ON DELETE CASCADE,
    FOREIGN KEY (participant_id) REFERENCES participants(id) ON DELETE CASCADE,
    UNIQUE (event_id, participant_id)
);
