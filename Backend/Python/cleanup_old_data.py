import mariadb
from datetime import datetime, timedelta
import pytz

def cleanup_old_data(json_database_details):
    """
    Deletes entries older than 30 days from the interface_stats_history table.
    """
    conn = None
    try:
        conn = mariadb.connect(
            host=json_database_details['host'],
            user=json_database_details['username'],
            password=json_database_details['password'],
            database=json_database_details['database']
        )
        cursor = conn.cursor()

        spanish_timezone = pytz.timezone('Europe/Madrid')

        cutoff_date = (datetime.now(spanish_timezone) - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

        delete_query = "DELETE FROM interface_stats_history WHERE archived_at < ?"
        cursor.execute(delete_query, (cutoff_date,))
        deleted_rows = cursor.rowcount
        conn.commit()

        print(f"Deleted {deleted_rows} entries older than 30 days from interface_stats_history.")

    except mariadb.Error as e:
        print(f"Error deleting old entries from MariaDB: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    json_database_details = {
        "host": "localhost",
        "username": "logger",
        "password": "logger_password",
        "database": "ciscoLogger"
    }

    cleanup_old_data(json_database_details)