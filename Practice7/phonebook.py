import psycopg2
import csv
from connect import connect
print("1 - create table")
print("2 - insert contact")
print("3 - insert contact from csv")
print("4 - find contact")
print("5 - update contact")
print("6 - delete contact")
do = input("command: ")
def create_table():
    conn = connect()

    if conn is None:
        print("No connection")
        return
    
    try:
        cur = conn.cursor()

        cur.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(11) NOT NULL UNIQUE
                    )
                """)
        conn.commit()
        print("Table created")

        cur.close()
        conn.close()
    except Exception as error:
        print("error: ", error)
        conn.rollback()
        conn.close()

def insert_contact():
    conn = connect()
    if conn is None:
        print("No connection")
        return
    
    try:
        cur = conn.cursor()

        name = input("enter name: ")
        phone = input("enter phone numbers: ")
        
        cur.execute(
            "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
        )
        conn.commit()
        cur.close()
        conn.close()

    except Exception as error:
        print("Error: ", error)
        conn.rollback()
        conn.close()


def insert_contact_from_csv(name):
    conn = connect()

    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()
        with open(name, "r") as f:
            reader = csv.reader(f)

            next(reader)

            for row in reader:
                cur.execute(
                    "INSERT INTO contacts (name, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING",
                    (row[0], row[1])
                )
        conn.commit()
        print("Data inserted from CSV")

        cur.close()
        conn.close()

    except Exception as error:
        print("Error:", error)
        conn.rollback()
        conn.close()

def query_contacts():
    print("1 - show all")
    print("2 - search by name")
    print("3 - search by phone prefix")

    choice = input("Choose option: ").strip()

    conn = connect()

    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()

        if choice == "1":
            cur.execute("SELECT * FROM contacts")

        elif choice == "2":
            name = input("Enter name: ")
            cur.execute(
                "SELECT * FROM contacts WHERE name ILIKE %s",
                (name,)
            )

        elif choice == "3":
            prefix = input("Enter phone prefix: ")
            cur.execute(
                "SELECT * FROM contacts WHERE phone LIKE %s",
                (prefix + "%",)
            )

        else:
            print("Invalid option")
            return

        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("No contacts found")

        cur.close()
        conn.close()

    except Exception as error:
        print("Error:", error)

def update_contact():
    search_value = input("Enter current name or phone: ").strip()

    print("1 - update name")
    print("2 - update phone")
    choice = input("Choose option: ").strip()

    conn = connect()

    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()

        if choice == "1":
            new_name = input("Enter new name: ").strip()

            cur.execute(
                "UPDATE contacts SET name = %s WHERE name = %s OR phone = %s",
                (new_name, search_value, search_value)
            )

        elif choice == "2":
            new_phone = input("Enter new phone: ").strip()

            cur.execute(
                "UPDATE contacts SET phone = %s WHERE name = %s OR phone = %s",
                (new_phone, search_value, search_value)
            )

        else:
            print("Invalid option")
            return

        conn.commit()
        print("Updated rows:", cur.rowcount)

        cur.close()
        conn.close()

    except Exception as error:
        print("Error:", error)
        conn.rollback()
        conn.close()

def delete_contact():
    value = input("Enter name or phone to delete: ").strip()

    conn = connect()

    if conn is None:
        print("No connection")
        return

    try:
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM contacts WHERE name = %s OR phone = %s",
            (value, value)
        )

        conn.commit()
        print("Deleted rows:", cur.rowcount)

        cur.close()
        conn.close()

    except Exception as error:
        print("Error:", error)
        conn.rollback()
        conn.close()

if do == "1":
    create_table()
elif do == "2":
    insert_contact()
elif do == "3":
    insert_contact_from_csv("contacts.csv")
elif do == "4":
    query_contacts()
elif do == "5":
    update_contact()
elif do == "6":
    delete_contact()
else:
    print("unknown command")