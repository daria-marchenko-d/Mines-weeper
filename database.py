import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('minesweeper.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                time INTEGER,
                status TEXT,
                flags_used INTEGER,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(player_id) REFERENCES players(id)
            )
        ''')
        self.conn.commit()

    def add_player(self, name):
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO players (name) VALUES (?)', (name,))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM players WHERE name = ?', (name,))
            return cursor.fetchone()[0]

    def add_score(self, player_id, time, status, flags_used, difficulty):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO scores (player_id, time, status, flags_used, difficulty)
            VALUES (?, ?, ?, ?, ?)
        ''', (player_id, time, status, flags_used, difficulty))
        self.conn.commit()

    def get_scores(self, player_id=None):
        cursor = self.conn.cursor()
        if player_id:
            cursor.execute('''
                SELECT s.time, s.status, s.flags_used, s.difficulty, s.created_at
                FROM scores s
                WHERE s.player_id = ?
                ORDER BY s.created_at DESC
            ''', (player_id,))
        else:
            cursor.execute('''
                SELECT p.name, s.time, s.status, s.flags_used, s.difficulty, s.created_at
                FROM scores s
                JOIN players p ON s.player_id = p.id
                ORDER BY s.created_at DESC
                LIMIT 10
            ''')
        return cursor.fetchall()

    def delete_player_data(self, player_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM scores WHERE player_id = ?', (player_id,))
        cursor.execute('DELETE FROM players WHERE id = ?', (player_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()