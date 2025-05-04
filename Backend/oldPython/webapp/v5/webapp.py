"""from flask import Flask, render_template, request
import mariadb
import os
import math

app = Flask(__name__)

# Database connection details (adjust these based on your MariaDB setup)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "logger")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "logger")
DB_NAME = os.environ.get("DB_NAME", "ciscoLogger")
RECORDS_PER_PAGE = 48

def get_db_connection():
    conn = None
    try:
        conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
    return conn

def get_total_interface_count(conn, search_term=None):
    cursor = conn.cursor()
    query = "SELECT COUNT(DISTINCT interface_name) FROM interface_stats"
    if search_term:
        query += " WHERE interface_name LIKE %s OR description LIKE %s OR vlan LIKE %s OR mac LIKE %s OR status LIKE %s OR switchport LIKE %s OR switch LIKE %s"
        cursor.execute(query, ('%' + search_term + '%',) * 7)
    else:
        cursor.execute(query)
    return cursor.fetchone()[0]

def get_paginated_interfaces(conn, page, search_term=None):
    offset = (page - 1) * RECORDS_PER_PAGE
    cursor = conn.cursor()
    query = '''
    SELECT interface_name, MAX(last_input), MAX(last_output), MAX(log_time), MAX(description),
           MAX(duplex_status), MAX(speed), MAX(vlan), MAX(mac), MAX(status), MAX(switchport), MAX(switch)
    FROM interface_stats
    '''
    where_clause = ""
    if search_term:
        where_conditions = [
            "interface_name LIKE %s",
            "description LIKE %s",
            "vlan LIKE %s",
            "mac LIKE %s",
            "status LIKE %s",
            "switchport LIKE %s",
            "switch LIKE %s"
        ]
        where_clause = " WHERE " + " OR ".join(where_conditions)

    group_by_order_limit_offset = '''
    GROUP BY interface_name
    ORDER BY
        SUBSTRING_INDEX(interface_name, '/', 1),
        CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(interface_name, '/', 2), '/', -1) AS UNSIGNED),
        CAST(SUBSTRING_INDEX(interface_name, '/', -1) AS UNSIGNED)
    LIMIT %s OFFSET %s
    '''

    full_query = query + where_clause + group_by_order_limit_offset

    if search_term:
        cursor.execute(full_query, ('%' + search_term + '%',) * 7 + (RECORDS_PER_PAGE, offset))
    else:
        cursor.execute(full_query, (RECORDS_PER_PAGE, offset))

    return cursor.fetchall()

@app.route("/", defaults={'page': 1})
@app.route("/page/<int:page>")
def display_interface_stats(page):
    search_term = request.args.get('search')
    conn = get_db_connection()
    if conn:
        total_interfaces = get_total_interface_count(conn, search_term)
        total_pages = math.ceil(total_interfaces / RECORDS_PER_PAGE)
        interface_data = get_paginated_interfaces(conn, page, search_term)
        conn.close()
        return render_template("interface_stats.html",
                               interface_data=interface_data,
                               current_page=page,
                               total_pages=total_pages,
                               search_term=search_term)
    else:
        return "Failed to connect to the database."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")"""

from flask import Flask, render_template, request
import mariadb
import os
import math

app = Flask(__name__)

# Database connection details (adjust these based on your MariaDB setup)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "logger")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "logger")
DB_NAME = os.environ.get("DB_NAME", "ciscoLogger")
RECORDS_PER_PAGE = 48
HISTORY_RECORDS_PER_PAGE = 20  # Número de registros históricos por página

def get_db_connection():
    conn = None
    try:
        conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
    return conn

def get_total_interface_count(conn, search_term=None):
    cursor = conn.cursor()
    query = "SELECT COUNT(DISTINCT interface_name) FROM interface_stats"
    if search_term:
        query += " WHERE interface_name LIKE %s OR description LIKE %s OR vlan LIKE %s OR mac LIKE %s OR status LIKE %s OR switchport LIKE %s OR switch LIKE %s"
        cursor.execute(query, ('%' + search_term + '%',) * 7)
    else:
        cursor.execute(query)
    return cursor.fetchone()[0]

def get_paginated_interfaces(conn, page, search_term=None):
    offset = (page - 1) * RECORDS_PER_PAGE
    cursor = conn.cursor()
    query = """
    SELECT interface_name, MAX(last_input), MAX(last_output), MAX(log_time), MAX(description),
           MAX(duplex_status), MAX(speed), MAX(vlan), MAX(mac), MAX(status), MAX(switchport), MAX(switch)
    FROM interface_stats
    """
    where_clause = ""
    if search_term:
        where_conditions = [
            "interface_name LIKE %s",
            "description LIKE %s",
            "vlan LIKE %s",
            "mac LIKE %s",
            "status LIKE %s",
            "switchport LIKE %s",
            "switch LIKE %s"
        ]
        where_clause = " WHERE " + " OR ".join(where_conditions)

    group_by_order_limit_offset = """
    GROUP BY interface_name
    ORDER BY
        SUBSTRING_INDEX(interface_name, '/', 1),
        CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(interface_name, '/', 2), '/', -1) AS UNSIGNED),
        CAST(SUBSTRING_INDEX(interface_name, '/', -1) AS UNSIGNED)
    LIMIT %s OFFSET %s
    """

    full_query = query + where_clause + group_by_order_limit_offset

    if search_term:
        cursor.execute(full_query, ('%' + search_term + '%',) * 7 + (RECORDS_PER_PAGE, offset))
    else:
        cursor.execute(full_query, (RECORDS_PER_PAGE, offset))

    return cursor.fetchall()

def get_total_history_count(conn, interface_name):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM interface_stats WHERE interface_name = %s", (interface_name,))
    return cursor.fetchone()[0]

def get_interface_history(conn, interface_name, page):
    offset = (page - 1) * HISTORY_RECORDS_PER_PAGE
    cursor = conn.cursor()
    cursor.execute("""
        SELECT last_input, last_output, log_time, description, duplex_status, speed, vlan, mac, status, switchport, switch
        FROM interface_stats
        WHERE interface_name = %s
        ORDER BY log_time DESC
        LIMIT %s OFFSET %s
    """, (interface_name, HISTORY_RECORDS_PER_PAGE, offset))
    return cursor.fetchall()

@app.route("/", defaults={'page': 1})
@app.route("/page/<int:page>")
def display_interface_stats(page):
    search_term = request.args.get('search')
    conn = get_db_connection()
    if conn:
        total_interfaces = get_total_interface_count(conn, search_term)
        total_pages = math.ceil(total_interfaces / RECORDS_PER_PAGE)
        interface_data = get_paginated_interfaces(conn, page, search_term)
        conn.close()
        return render_template("interface_stats.html",
                               interface_data=interface_data,
                               current_page=page,
                               total_pages=total_pages,
                               search_term=search_term)
    else:
        return "Failed to connect to the database."

@app.route("/history/<interface_name>", defaults={'page': 1})
@app.route("/history/<interface_name>/page/<int:page>")
def display_interface_history(interface_name, page):
    conn = get_db_connection()
    if conn:
        total_records = get_total_history_count(conn, interface_name)
        total_pages = math.ceil(total_records / HISTORY_RECORDS_PER_PAGE)
        history_data = get_interface_history(conn, interface_name, page)
        conn.close()
        return render_template("interface_history.html",
                               interface_name=interface_name,
                               history_data=history_data,
                               current_page=page,
                               total_pages=total_pages)
    else:
        return "Failed to connect to the database."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")