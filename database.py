import sqlite3

database = sqlite3.connect('pogoda.db')
cursor = database.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS history(
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT,
    temp TEXT,
    city_name TEXT,
    wind TEXT,
    sunrise TEXT,
    sunset TEXT,
    descriptionn TEXT
);
''')

database.commit()
database.close()