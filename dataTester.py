import sqlite3

try:
    sqliteConnection = sqlite3.connect('heads_up_database.db')
    cursor = sqliteConnection.cursor()
    cursor.execute("SELECT * FROM card_history")
    record = cursor.fetchall()
    print(record)
    cursor.close()

except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
finally:
    if (sqliteConnection):
        sqliteConnection.close()
        print("The SQLite connection is closed")
