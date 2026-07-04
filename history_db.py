import sqlite3

DATABASE = "scan_history.db"


def initialize_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            project_name TEXT,

            scan_date TEXT,

            overall_score INTEGER,

            total_files INTEGER,

            total_lines INTEGER,

            warnings INTEGER
        )
    """)

    connection.commit()
    connection.close()


def save_scan(
    project_name,
    scan_date,
    overall_score,
    total_files,
    total_lines,
    warnings
):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""

        INSERT INTO scan_history(

            project_name,
            scan_date,
            overall_score,
            total_files,
            total_lines,
            warnings

        )

        VALUES(?,?,?,?,?,?)

    """, (

        project_name,
        scan_date,
        overall_score,
        total_files,
        total_lines,
        warnings

    ))

    connection.commit()
    connection.close()


def get_history():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""

        SELECT *

        FROM scan_history

        ORDER BY id DESC

    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


def delete_scan(scan_id):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute(

        "DELETE FROM scan_history WHERE id=?",

        (scan_id,)

    )

    connection.commit()
    connection.close()


def clear_history():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute(

        "DELETE FROM scan_history"

    )

    connection.commit()
    connection.close()


def search_history(keyword):

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(

        """

        SELECT *

        FROM scan_history

        WHERE project_name LIKE ?

        ORDER BY id DESC

        """,

        ("%" + keyword + "%",)

    )

    rows = cursor.fetchall()

    connection.close()

    return rows


def history_summary():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""

        SELECT

            COUNT(*) AS total_scans,

            MAX(overall_score) AS best_score,

            ROUND(AVG(overall_score),1) AS average_score

        FROM scan_history

    """)

    summary = cursor.fetchone()

    connection.close()

    return summary