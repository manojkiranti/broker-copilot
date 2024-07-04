from django.db import connection, OperationalError

def check_database_connection():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except OperationalError as e:
        print(f"Error connecting to database: {e}")
        return False
check_database_connection()