PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    email   TEXT UNIQUE NOT NULL,
    code    TEXT NOT NULL,
    role    TEXT NOT NULL CHECK (role IN ('organizer', 'student'))
);

CREATE TABLE events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    building    TEXT NOT NULL,
    room        TEXT NOT NULL,
    event_date  TEXT NOT NULL,
    start_time  TEXT NOT NULL,
    end_time    TEXT NOT NULL
);

CREATE TABLE items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id     INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    icon         TEXT NOT NULL,
    total_qty    INTEGER NOT NULL,
    remaining_qty INTEGER NOT NULL,
    expires_at   TEXT NOT NULL
);

CREATE TABLE claims (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id    INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    qty        INTEGER NOT NULL,
    claimed_at TEXT NOT NULL
);

-- Seed users
INSERT INTO users (email, code, role) VALUES
('alice@campus.edu', '1234', 'organizer'),
('bob@campus.edu',   '5678', 'student');

-- Seed events
INSERT INTO events (title, building, room, event_date, start_time, end_time) VALUES
('CS Study Jam Snacks',        'Computer Science Building', 'CS 209', '2025-12-05', '14:00', '16:00'),
('Late Night Pizza Social',    'Havener Center',            'Atrium', '2025-12-05', '19:00', '21:00'),
('Library De-Stress Bites',    'Curtis Laws Wilson Library','2nd Floor Lounge','2025-12-06','10:00','12:00'),
('Toomey Hall Grab & Go',      'Toomey Hall',               '120',    '2025-12-06','12:00','13:30');

-- Seed items (simple Apple-style minimal set)
INSERT INTO items (event_id, name, icon, total_qty, remaining_qty, expires_at) VALUES
(1, 'Chicken Sandwich', 'sandwich', 20, 20, '2025-12-05 16:00'),
(1, 'Veggie Sandwich',  'sandwich', 15, 15, '2025-12-05 16:00'),
(1, 'Soda',             'soda',     30, 30, '2025-12-05 16:00'),
(1, 'Water',            'water',    24, 24, '2025-12-05 16:00'),

(2, 'Cheese Pizza Slice','pizza',   40, 40, '2025-12-05 21:00'),
(2, 'Veggie Pizza Slice','pizza',   32, 32, '2025-12-05 21:00'),
(2, 'Brownie',           'brownie', 25, 25, '2025-12-05 21:00'),

(3, 'Fruit Cup',         'fruit',   30, 30, '2025-12-06 12:00'),
(3, 'Granola Bar',       'brownie', 30, 30, '2025-12-06 12:00'),
(3, 'Water',             'water',   20, 20, '2025-12-06 12:00'),

(4, 'Chicken Sandwich',  'sandwich', 18, 18, '2025-12-06 13:30'),
(4, 'Ham Sandwich',      'sandwich', 18, 18, '2025-12-06 13:30'),
(4, 'Soda',              'soda',     24, 24, '2025-12-06 13:30'),
(4, 'Water',             'water',    24, 24, '2025-12-06 13:30');
