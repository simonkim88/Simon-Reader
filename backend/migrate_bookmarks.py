import sqlite3

def migrate():
    conn = sqlite3.connect('simon_reader.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE bookmarks ADD COLUMN comment TEXT")
        print("Migration successful: Added comment column to bookmarks table.")
    except sqlite3.OperationalError as e:
        print(f"Migration failed or column already exists: {e}")
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    migrate()
