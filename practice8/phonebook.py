from connect import get_connection


def insert_or_update():
    name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    conn.commit()

    cur.close()
    conn.close()

    print("Contact inserted or updated.")


def search():
    pattern = input("Search: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    rows = cur.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No contacts found.")

    cur.close()
    conn.close()


def paginate():
    limit = int(input("Limit: "))
    offset = int(input("Offset: "))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
    rows = cur.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No contacts found.")

    cur.close()
    conn.close()


def delete():
    value = input("Enter name or phone to delete: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL delete_contact(%s)", (value,))
    conn.commit()

    cur.close()
    conn.close()

    print("Contact deleted if it existed.")


def bulk_insert():
    n = int(input("How many contacts: "))

    names = []
    phones = []

    for i in range(n):
        print(f"\nContact {i + 1}")
        name = input("Name: ").strip()
        phone = input("Phone: ").strip()

        names.append(name)
        phones.append(phone)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT bulk_insert_contacts(%s::TEXT[], %s::TEXT[])",
        (names, phones)
    )

    invalid_data = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    if invalid_data:
        print("Invalid entries:")
        for item in invalid_data:
            print(item)
    else:
        print("All contacts inserted successfully.")


def menu():
    while True:
        print("\n--- PhoneBook Practice 8 ---")
        print("1. Insert or Update")
        print("2. Search")
        print("3. Pagination")
        print("4. Delete")
        print("5. Bulk Insert")
        print("0. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            insert_or_update()
        elif choice == "2":
            search()
        elif choice == "3":
            paginate()
        elif choice == "4":
            delete()
        elif choice == "5":
            bulk_insert()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()