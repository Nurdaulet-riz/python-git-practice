import csv
import json
from datetime import datetime
from pathlib import Path

from connect import connect

PHONE_TYPES = {"home", "work", "mobile"}
SORT_FIELDS = {"name": "c.name", "birthday": "c.birthday", "date": "c.created_at"}


def run_sql_file(filename):
    conn = connect()
    if conn is None:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                with open(filename, "r", encoding="utf-8") as file:
                    cur.execute(file.read())
        print(f"{filename} executed successfully")
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def setup_database():
    run_sql_file("schema.sql")
    run_sql_file("procedures.sql")
    run_sql_file("functions.sql")


def normalize_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Birthday must be in YYYY-MM-DD format")


def normalize_phone_type(value):
    value = (value or "mobile").strip().lower()
    if value not in PHONE_TYPES:
        raise ValueError("Phone type must be home, work or mobile")
    return value


def get_or_create_group(cur, group_name):
    group_name = (group_name or "Other").strip() or "Other"
    group_name = group_name.capitalize()

    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )
    cur.execute("SELECT id FROM groups WHERE LOWER(name) = LOWER(%s)", (group_name,))
    return cur.fetchone()[0]


def contact_exists(cur, name):
    cur.execute("SELECT id FROM contacts WHERE LOWER(name) = LOWER(%s)", (name,))
    row = cur.fetchone()
    return row[0] if row else None


def save_contact(cur, name, email, birthday, group_name, phones, overwrite=False):
    if not name or not name.strip():
        raise ValueError("Name cannot be empty")

    name = name.strip()
    birthday = normalize_date(birthday) if isinstance(birthday, str) else birthday
    group_id = get_or_create_group(cur, group_name)
    existing_id = contact_exists(cur, name)

    if existing_id and not overwrite:
        return "skipped"

    if existing_id and overwrite:
        cur.execute(
            """
            UPDATE contacts
            SET email = %s, birthday = %s, group_id = %s
            WHERE id = %s
            """,
            (email, birthday, group_id, existing_id)
        )
        cur.execute("DELETE FROM phones WHERE contact_id = %s", (existing_id,))
        contact_id = existing_id
        result = "overwritten"
    else:
        cur.execute(
            """
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, email, birthday, group_id)
        )
        contact_id = cur.fetchone()[0]
        result = "inserted"

    for item in phones:
        phone = (item.get("phone") or "").strip()
        phone_type = normalize_phone_type(item.get("type"))
        if phone:
            cur.execute(
                "INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, phone, phone_type)
            )

    return result


def print_rows(rows):
    if not rows:
        print("No contacts found")
        return

    for row in rows:
        print("-" * 80)
        print(f"ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"Email: {row[2] or ''}")
        print(f"Birthday: {row[3] or ''}")
        print(f"Group: {row[4] or ''}")
        print(f"Phones: {row[5] or ''}")
    print("-" * 80)


def filter_by_group():
    group_name = input("Enter group name: ").strip()
    conn = connect()
    if conn is None:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM search_contacts(%s)
                WHERE LOWER(group_name) = LOWER(%s)
                """,
                (group_name, group_name)
            )
            print_rows(cur.fetchall())
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def search_by_email():
    query = input("Enter email part, for example gmail: ").strip()
    conn = connect()
    if conn is None:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM search_contacts(%s)
                WHERE email ILIKE %s
                """,
                (query, f"%{query}%")
            )
            print_rows(cur.fetchall())
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def sort_contacts():
    sort_key = input("Sort by name, birthday or date: ").strip().lower()
    if sort_key not in SORT_FIELDS:
        print("Unknown sort field")
        return

    conn = connect()
    if conn is None:
        return

    sql = f"""
        SELECT
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name AS group_name,
            COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id), '') AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
        ORDER BY {SORT_FIELDS[sort_key]} NULLS LAST
    """

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            print_rows(cur.fetchall())
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def search_all_fields():
    query = input("Enter name, email, group or phone part: ").strip()
    conn = connect()
    if conn is None:
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            print_rows(cur.fetchall())
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def paginated_navigation():
    try:
        limit_value = int(input("Page size: ").strip())
    except ValueError:
        print("Page size must be a number")
        return

    offset = 0
    conn = connect()
    if conn is None:
        return

    try:
        while True:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit_value, offset))
                rows = cur.fetchall()
                print(f"\nPage offset: {offset}")
                print_rows(rows)

            command = input("next / prev / quit: ").strip().lower()
            if command == "next":
                offset += limit_value
            elif command == "prev":
                offset = max(0, offset - limit_value)
            elif command == "quit":
                break
            else:
                print("Unknown command")
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def add_phone_console():
    name = input("Contact name: ").strip()
    phone = input("New phone: ").strip()
    phone_type = input("Type home/work/mobile: ").strip().lower()

    conn = connect()
    if conn is None:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        print("Phone added")
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def move_to_group_console():
    name = input("Contact name: ").strip()
    group_name = input("New group: ").strip()

    conn = connect()
    if conn is None:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        print("Contact moved")
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def export_to_json():
    filename = input("JSON file name for export: ").strip() or "contacts.json"
    conn = connect()
    if conn is None:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.id, c.name, c.email, c.birthday, g.name, c.created_at
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                ORDER BY c.id
                """
            )
            contacts = []
            for contact_id, name, email, birthday, group_name, created_at in cur.fetchall():
                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
                    (contact_id,)
                )
                phones = [{"phone": p, "type": t} for p, t in cur.fetchall()]
                contacts.append({
                    "name": name,
                    "email": email,
                    "birthday": birthday.isoformat() if birthday else None,
                    "group": group_name,
                    "created_at": created_at.isoformat() if created_at else None,
                    "phones": phones
                })

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(contacts, file, indent=4, ensure_ascii=False)
        print(f"Exported to {filename}")
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def import_from_json():
    filename = input("JSON file name for import: ").strip()
    path = Path(filename)
    if not path.exists():
        print("File does not exist")
        return

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    conn = connect()
    if conn is None:
        return

    inserted = skipped = overwritten = 0

    try:
        with conn:
            with conn.cursor() as cur:
                for item in data:
                    name = item.get("name", "").strip()
                    exists = contact_exists(cur, name)
                    overwrite = False

                    if exists:
                        answer = input(f"Contact '{name}' already exists. skip/overwrite? ").strip().lower()
                        if answer == "overwrite":
                            overwrite = True
                        else:
                            skipped += 1
                            continue

                    result = save_contact(
                        cur,
                        name=name,
                        email=item.get("email"),
                        birthday=item.get("birthday"),
                        group_name=item.get("group"),
                        phones=item.get("phones", []),
                        overwrite=overwrite
                    )

                    if result == "inserted":
                        inserted += 1
                    elif result == "overwritten":
                        overwritten += 1
                    else:
                        skipped += 1

        print(f"Inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}")
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def import_from_csv():
    filename = input("CSV file name: ").strip() or "contacts.csv"
    path = Path(filename)
    if not path.exists():
        print("File does not exist")
        return

    conn = connect()
    if conn is None:
        return

    inserted = overwritten = skipped = 0

    try:
        with conn:
            with conn.cursor() as cur:
                with open(path, "r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        name = row.get("name", "").strip()
                        exists = contact_exists(cur, name)
                        overwrite = bool(exists)

                        result = save_contact(
                            cur,
                            name=name,
                            email=row.get("email"),
                            birthday=row.get("birthday"),
                            group_name=row.get("group"),
                            phones=[{"phone": row.get("phone"), "type": row.get("type")}],
                            overwrite=overwrite
                        )

                        if result == "inserted":
                            inserted += 1
                        elif result == "overwritten":
                            overwritten += 1
                        else:
                            skipped += 1

        print(f"CSV import finished. Inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}")
    except Exception as error:
        print("Error:", error)
    finally:
        conn.close()


def menu():
    while True:
        print("\nPHONEBOOK TSIS 1")
        print("1 - setup database schema and routines")
        print("2 - search by name/email/group/phone")
        print("3 - filter by group")
        print("4 - search by email")
        print("5 - sort contacts")
        print("6 - paginated navigation")
        print("7 - add phone to existing contact")
        print("8 - move contact to group")
        print("9 - export to JSON")
        print("10 - import from JSON")
        print("11 - import from CSV")
        print("0 - quit")

        command = input("Choose command: ").strip()

        if command == "1":
            setup_database()
        elif command == "2":
            search_all_fields()
        elif command == "3":
            filter_by_group()
        elif command == "4":
            search_by_email()
        elif command == "5":
            sort_contacts()
        elif command == "6":
            paginated_navigation()
        elif command == "7":
            add_phone_console()
        elif command == "8":
            move_to_group_console()
        elif command == "9":
            export_to_json()
        elif command == "10":
            import_from_json()
        elif command == "11":
            import_from_csv()
        elif command == "0":
            break
        else:
            print("Unknown command")


if __name__ == "__main__":
    menu()
