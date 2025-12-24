import sqlite3

def migrate():
    conn = sqlite3.connect('simon_reader.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS highlights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                selected_text TEXT,
                cfi_range VARCHAR,
                color VARCHAR DEFAULT 'yellow',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(book_id) REFERENCES books(id)
            )
        """)
        conn.commit()
        print("Successfully created highlights table.")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
