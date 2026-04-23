import psycopg2
import csv
from config import DB_CONFIG

def get_connection():
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )


def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(20) UNIQUE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Table 'phonebook' is ready.")


def add_contact(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO phonebook (name, phone)
        VALUES (%s, %s)
        ON CONFLICT (phone) DO NOTHING;
    """, (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Added contact: {name} - {phone}")


def show_contacts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phonebook ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for row in rows:
        print(row)


def update_contact(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE phonebook
        SET phone=%s
        WHERE name=%s;
    """, (phone, name))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Updated {name} with new phone: {phone}")


def delete_contact(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM phonebook WHERE name=%s;", (name,))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Deleted contact: {name}")

def find_contact(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phonebook WHERE name=%s;", (name,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    if rows:
        for row in rows:
            print(row)
    else:
        print(f"No contact found with name: {name}")

def import_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            add_contact(row['name'], row['phone'])
    print(f"Contacts from {csv_file} imported successfully.")


def menu():
    while True:
        print("\n   PhoneBook Menu   ")
        print("1. Add contact manually")
        print("2. Insert contacts from CSV")
        print("3. Update contact")
        print("4. Delete contact")
        print("5. Search contacts")
        print("6. Exit")
        choice = input("Choose an option (1-6): ")

        if choice == "1":
            name = input("Name: ")
            phone = input("Telephone: ")
            add_contact(name, phone)
        elif choice == "2":
            show_contacts()
        elif choice == "3":
            name = input("The name of the contact that needs updating:")
            phone = input("New telephone: ")
            update_contact(name, phone)
        elif choice == "4":
            name = input("The name of the contact to delete: ")
            delete_contact(name)
        elif choice == "5":
            name = input("Search name: ")
            find_contact(name)
        elif choice == "6":
            print("Exit from the programme")
            break
        else:
            print("Wrong choice, try again.")

if __name__ == "__main__":
    create_table()
    menu()