"""Minimal SQLite database for avatar game persistence"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / 'avatar_game.db'

def init_db():
    """Initialize database with minimal schema"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (avatar_id TEXT, user_msg TEXT, avatar_msg TEXT, 
                  sentiment TEXT, timestamp INTEGER, score INTEGER)''')
    conn.commit()
    conn.close()

def save_message(avatar_id, user_msg, avatar_msg, sentiment, timestamp, score):
    """Save single message"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO conversations VALUES (?,?,?,?,?,?)',
              (avatar_id, user_msg, avatar_msg, sentiment, timestamp, score))
    conn.commit()
    conn.close()

def load_memory(avatar_id):
    """Load last 20 messages for avatar"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM conversations WHERE avatar_id=? ORDER BY timestamp DESC LIMIT 20',
              (avatar_id,))
    rows = c.fetchall()
    conn.close()
    return [{'user': r[1], 'avatar': r[2], 'sentiment': r[3], 
             'timestamp': r[4], 'score': r[5]} for r in reversed(rows)]

def get_relationship_score(avatar_id):
    """Get total relationship score"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT SUM(score) FROM conversations WHERE avatar_id=?', (avatar_id,))
    result = c.fetchone()[0] or 0
    conn.close()
    return result

init_db()
