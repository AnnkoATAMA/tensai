DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS players;


CREATE TABLE users (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       name VARCHAR(255) NOT NULL,
                       email VARCHAR(255) NOT NULL,
                       password VARCHAR(255) NOT NULL,
                       created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                       updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE rooms (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       max_players INT NOT NULL CHECK (max_players IN (3, 4)),
                       game_type ENUM('sanma', 'yonma') NOT NULL
);

CREATE TABLE players (
                         id INT AUTO_INCREMENT PRIMARY KEY,
                         user_id INT NOT NULL,
                         room_id INT NOT NULL,
                         FOREIGN KEY (user_id) REFERENCES users(id),
                         FOREIGN KEY (room_id) REFERENCES rooms(id),
                         UNIQUE KEY unique_user_room (user_id, room_id)
);