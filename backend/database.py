
import sqlite3
import os
from datetime import datetime

DB_NAME = "food_monitor.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Readings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            gas_level INTEGER,
            temperature REAL,
            humidity REAL,
            status TEXT
        )
    ''')
    
    # Slots table (for fruits/vegetables)
    c.execute('''
        CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            image_path TEXT,
            last_checked DATETIME,
            is_spoiled BOOLEAN DEFAULT 0
        )
    ''')
    
    # Initialize some default slots if empty
    c.execute('SELECT count(*) FROM slots')
    if c.fetchone()[0] == 0:
        default_slots = [
            ('Apple', 'Fruit', 'static/images/apple_placeholder.png', None, False),
            ('Banana', 'Fruit', 'static/images/banana_placeholder.png', None, False),
            ('Carrot', 'Vegetable', 'static/images/carrot_placeholder.png', None, False),
            ('Tomato', 'Vegetable', 'static/images/tomato_placeholder.png', None, False)
        ]
        c.executemany('INSERT INTO slots (name, type, image_path, last_checked, is_spoiled) VALUES (?, ?, ?, ?, ?)', default_slots)
        
    conn.commit()
    conn.close()
    print("Database initialized.")

def log_reading(gas, temp, hum, status):
    conn = get_db_connection()
    conn.execute('INSERT INTO readings (gas_level, temperature, humidity, status) VALUES (?, ?, ?, ?)',
                 (gas, temp, hum, status))
    conn.commit()
    conn.close()

def get_latest_reading():
    conn = get_db_connection()
    reading = conn.execute('SELECT * FROM readings ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    return dict(reading) if reading else None

def get_all_slots():
    conn = get_db_connection()
    slots = conn.execute('SELECT * FROM slots').fetchall()
    conn.close()
    return [dict(s) for s in slots]

def update_slot_image(slot_id, image_path):
    conn = get_db_connection()
    conn.execute('UPDATE slots SET image_path = ?, last_checked = ? WHERE id = ?', 
                 (image_path, datetime.now(), slot_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
