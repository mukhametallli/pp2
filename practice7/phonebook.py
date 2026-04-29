import csv
from connect import get_connection


def create_table():
    sql = """
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) UNIQUE NOT NULL
    );
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        print("Table is ready.")

    except Exception as e:
        print("Create table error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
def insert_contact(first_name, phone):
    sql = """
    INSERT INTO phonebook (first_name, phone)
    VALUES (%s, %s)
    ON CONFLICT (phone) DO NOTHING;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (first_name, phone))
        conn.commit()
        print("Contact inserted.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Insert error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def insert_from_csv(filename):
    sql = """
    INSERT INTO phonebook (first_name, phone)
    VALUES (%s, %s)
    ON CONFLICT (phone) DO NOTHING;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [(row["first_name"], row["phone"]) for row in reader]

        cur.executemany(sql, rows)
        conn.commit()
        print(f"{len(rows)} rows processed from CSV.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("CSV insert error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def insert_from_console():
    first_name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()
    insert_contact(first_name, phone)


def update_name_by_phone(phone, new_name):
    sql = """
    UPDATE phonebook
    SET first_name = %s
    WHERE phone = %s;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (new_name, phone))
        conn.commit()
        print("Name updated.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Update error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def update_phone_by_name(first_name, new_phone):
    sql = """
    UPDATE phonebook
    SET phone = %s
    WHERE first_name = %s;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (new_phone, first_name))
        conn.commit()
        print("Phone updated.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Update error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def query_all():
    sql = """
    SELECT id, first_name, phone
    FROM phonebook
    ORDER BY first_name;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print("Query error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def query_by_name(name_part):
    sql = """
    SELECT id, first_name, phone
    FROM phonebook
    WHERE first_name ILIKE %s
    ORDER BY first_name;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (f"%{name_part}%",))
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print("Query error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def query_by_phone_prefix(prefix):
    sql = """
    SELECT id, first_name, phone
    FROM phonebook
    WHERE phone LIKE %s
    ORDER BY first_name;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (f"{prefix}%",))
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print("Query error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def delete_by_name(first_name):
    sql = """
    DELETE FROM phonebook
    WHERE first_name = %s;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (first_name,))
        conn.commit()
        print("Deleted by name.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Delete error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def delete_by_phone(phone):
    sql = """
    DELETE FROM phonebook
    WHERE phone = %s;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (phone,))
        conn.commit()
        print("Deleted by phone.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Delete error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def menu():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Insert from console")
        print("2. Insert from CSV")
        print("3. Show all contacts")
        print("4. Search by name")
        print("5. Search by phone prefix")
        print("6. Update name by phone")
        print("7. Update phone by name")
        print("8. Delete by name")
        print("9. Delete by phone")
        print("0. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            insert_from_console()
        elif choice == "2":
            filename = input("CSV file name: ").strip()
            insert_from_csv(filename)
        elif choice == "3":
            query_all()
        elif choice == "4":
            name = input("Enter name part: ").strip()
            query_by_name(name)
        elif choice == "5":
            prefix = input("Enter phone prefix: ").strip()
            query_by_phone_prefix(prefix)
        elif choice == "6":
            phone = input("Current phone: ").strip()
            new_name = input("New name: ").strip()
            update_name_by_phone(phone, new_name)
        elif choice == "7":
            first_name = input("Current name: ").strip()
            new_phone = input("New phone: ").strip()
            update_phone_by_name(first_name, new_phone)
        elif choice == "8":
            first_name = input("Name to delete: ").strip()
            delete_by_name(first_name)
        elif choice == "9":
            phone = input("Phone to delete: ").strip()
            delete_by_phone(phone)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()

def insert_contact(first_name, phone):
    sql = """
    INSERT INTO phonebook (first_name, phone)
    VALUES (%s, %s)
    ON CONFLICT (phone) DO NOTHING;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (first_name, phone))
        conn.commit()
        print("Contact inserted.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Insert error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def insert_from_csv(filename):
    sql = """
    INSERT INTO phonebook (first_name, phone)
    VALUES (%s, %s)
    ON CONFLICT (phone) DO NOTHING;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [(row["first_name"], row["phone"]) for row in reader]

        cur.executemany(sql, rows)
        conn.commit()
        print(f"{len(rows)} rows processed from CSV.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("CSV insert error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def insert_from_console():
    first_name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()
    insert_contact(first_name, phone)


def update_name_by_phone(phone, new_name):
    sql = """
    UPDATE phonebook
    SET first_name = %s
    WHERE phone = %s;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (new_name, phone))
        conn.commit()
        print("Name updated.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Update error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def update_phone_by_name(first_name, new_phone):
    sql = """
    UPDATE phonebook
    SET phone = %s
    WHERE first_name = %s;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (new_phone, first_name))
        conn.commit()
        print("Phone updated.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Update error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def query_all():
    sql = """
    SELECT id, first_name, phone
    FROM phonebook
    ORDER BY first_name;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print("Query error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def query_by_name(name_part):
    sql = """
    SELECT id, first_name, phone
    FROM phonebook
    WHERE first_name ILIKE %s
    ORDER BY first_name;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (f"%{name_part}%",))
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print("Query error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def query_by_phone_prefix(prefix):
    sql = """
    SELECT id, first_name, phone
    FROM phonebook
    WHERE phone LIKE %s
    ORDER BY first_name;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (f"{prefix}%",))
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print("Query error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def delete_by_name(first_name):
    sql = """
    DELETE FROM phonebook
    WHERE first_name = %s;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (first_name,))
        conn.commit()
        print("Deleted by name.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Delete error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def menu():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Insert from console")
        print("2. Insert from CSV")
        print("3. Show all contacts")
        print("4. Search by name")
        print("5. Search by phone prefix")
        print("6. Update contact")
        print("7. Delete contact")
        print("0. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            insert_from_console()
        elif choice == "2":
            filename = input("CSV file name: ").strip()
            insert_from_csv(filename)
        elif choice == "3":
            query_all()
        elif choice == "4":
            name = input("Enter name part: ").strip()
            query_by_name(name)
        elif choice == "5":
            prefix = input("Enter phone prefix: ").strip()
            query_by_phone_prefix(prefix)
        elif choice == "6":
            name = input("Enter name: ").strip()
            new_phone = input("Enter new phone: ").strip()
            update_phone_by_name(name, new_phone)

        elif choice == "7":
            name = input("Enter name to delete: ").strip()
            delete_by_name(name)
        elif choice == "0":
            print("Goodbye.")
            
        
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    create_table()
    menu()