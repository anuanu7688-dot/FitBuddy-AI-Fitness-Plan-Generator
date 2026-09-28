import sqlite3

DATABASE_NAME = "fitbuddy.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            weight REAL NOT NULL,
            goal TEXT NOT NULL,
            intensity TEXT NOT NULL,
            plan TEXT,
            feedback TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_user(name, age, weight, goal, intensity, plan):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users
        (name, age, weight, goal, intensity, plan)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, age, weight, goal, intensity, plan))

    connection.commit()

    user_id = cursor.lastrowid

    connection.close()

    return user_id


def update_plan(user_id, plan, feedback):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET plan = ?, feedback = ?
        WHERE id = ?
    """, (plan, feedback, user_id))

    connection.commit()
    connection.close()
