import sqlite3

def check_schema():
    conn = sqlite3.connect('simon_reader.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(words)")
    columns = cursor.fetchall()
    print("Columns in 'words' table:")
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    check_schema()
