import psycopg2
from connect import connect


def create_support_tables():
    conn = connect()
    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS invalid_contacts (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                phone VARCHAR(50),
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
        print("Tables are ready")
    except Exception as error:
        conn.rollback()
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def create_db_routines():
    conn = connect()
    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()

        with open("functions.sql", "r", encoding="utf-8") as f:
            cur.execute(f.read())

        with open("procedures.sql", "r", encoding="utf-8") as f:
            cur.execute(f.read())

        conn.commit()
        print("Functions and procedures created")
    except Exception as error:
        conn.rollback()
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def search_contacts_by_pattern():
    pattern = input("Enter part of name or phone: ").strip()
    conn = connect()
    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("No matching contacts found")
    except Exception as error:
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def upsert_one_contact():
    name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()
    conn = connect()
    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()
        cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
        conn.commit()
        print("Procedure executed successfully")
    except Exception as error:
        conn.rollback()
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def insert_many_demo():
    names = ['Ali', 'Dana', 'Aruzhan', 'Test']
    phones = ['+77070000001', '12345', '+77070000003', '+77070000001']

    conn = connect()
    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()
        cur.execute("CALL insert_many_contacts(%s, %s)", (names, phones))
        conn.commit()

        cur.execute("SELECT name, phone, reason FROM invalid_contacts ORDER BY id")
        invalid_rows = cur.fetchall()
        print("Incorrect data:")
        for row in invalid_rows:
            print(row)
    except Exception as error:
        conn.rollback()
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def show_paginated_contacts():
    limit_value = int(input("Enter LIMIT: ").strip())
    offset_value = int(input("Enter OFFSET: ").strip())

    conn = connect()
    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM get_contacts_paginated(%s, %s)",
            (limit_value, offset_value)
        )
        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("No contacts on this page")
    except Exception as error:
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def delete_by_name_or_phone():
    value = input("Enter username or phone to delete: ").strip()
    conn = connect()
    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()
        cur.execute("CALL delete_contact_proc(%s)", (value,))
        conn.commit()
        print("Delete procedure executed")
    except Exception as error:
        conn.rollback()
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("1 - create tables")
    print("2 - create functions and procedures")
    print("3 - search by pattern")
    print("4 - upsert one contact")
    print("5 - insert many contacts")
    print("6 - pagination")
    print("7 - delete by name or phone")

    command = input("Choose command: ").strip()

    if command == "1":
        create_support_tables()
    elif command == "2":
        create_db_routines()
    elif command == "3":
        search_contacts_by_pattern()
    elif command == "4":
        upsert_one_contact()
    elif command == "5":
        insert_many_demo()
    elif command == "6":
        show_paginated_contacts()
    elif command == "7":
        delete_by_name_or_phone()
    else:
        print("Unknown command")
