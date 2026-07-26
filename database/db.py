import mysql.connector
from mysql.connector import Error

DB_HOST = 'localhost'
DB_USER = 'root'
PASSWORD = ''
DATABASE = 'central_bank_system'

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=PASSWORD,
            database=DATABASE
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_query(query, params=None):
    connection = get_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        return cursor
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def fetch_one(query, params=None):
    connection = get_connection()
    if connection is None:
        return None
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"Error fetching query: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def fetch_all(query, params=None):
    connection = get_connection()
    if connection is None:
        return None
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Error fetching query: {e}")
        return None
    finally:
        cursor.close()
        connection.close()
