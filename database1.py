import sqlite3

# Connect to SQLite database (will create it if it doesn't exist)
conn = sqlite3.connect('user_database.db')
cursor = conn.cursor()

# Create table
cursor.execute('''CREATE TABLE users
                  (username TEXT PRIMARY KEY,
                  password TEXT,
                  email TEXT,
                  reset_code INTEGER
               )''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Database created successfully!")
