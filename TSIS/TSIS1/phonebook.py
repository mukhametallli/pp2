# We import csv to read CSV files.
import csv

# We import json to read and write JSON files.
import json

# We import psycopg2 to work with PostgreSQL.
import psycopg2

# We import the database connection function.
from connect import get_connection


# This function runs an SQL file.
# For example: schema.sql or procedures.sql.
def execute_sql_file(filename):
    # Connect to the database.
    conn = get_connection()

    # Create a cursor. Cursor sends SQL commands.
    cur = conn.cursor()

    # Open the SQL file and read it.
    with open(filename, "r", encoding="utf-8") as file:
        # Run all SQL code from the file.
        cur.execute(file.read())

    # Save changes in the database.
    conn.commit()

    # Close cursor and connection.
    cur.close()
    conn.close()

    # Show message to the user.
    print(f"{filename} executed successfully")


# This function gets a group id.
# If the group does not exist, it creates a new group.
def get_or_create_group(cur, group_name):
    # If group name is empty, use "Other".
    if not group_name:
        group_name = "Other"

    # Add group to the table.
    # If this group already exists, do nothing.
    cur.execute("INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group_name,))

    # Find the id of this group.
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))

    # Return group id.
    return cur.fetchone()[0]


# This function adds a new contact.
# It can also update contact data if the name already exists.
def add_contact(first_name, email, birthday, group_name, phones):
    # Connect to the database.
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get group id or create this group.
        group_id = get_or_create_group(cur, group_name)

        # Add contact to contacts table.
        # If the contact name exists, update email, birthday, and group.
        cur.execute(
            """
            INSERT INTO contacts(first_name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (first_name) DO UPDATE
            SET email = EXCLUDED.email,
                birthday = EXCLUDED.birthday,
                group_id = EXCLUDED.group_id
            RETURNING id
            """,
            (first_name, email, birthday or None, group_id)
        )

        # Get id of the new or updated contact.
        contact_id = cur.fetchone()[0]

        # Add all phone numbers for this contact.
        for phone, phone_type in phones:
            # Add phone number.
            # If this phone already exists for this contact, update phone type.
            cur.execute(
                """
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
                ON CONFLICT (contact_id, phone) DO UPDATE
                SET type = EXCLUDED.type
                """,
                (contact_id, phone, phone_type)
            )

        # Save all changes.
        conn.commit()
        print("Contact saved successfully")

    except Exception as e:
        # If there is an error, cancel changes.
        conn.rollback()
        print("Error:", e)

    finally:
        # Always close cursor and connection.
        cur.close()
        conn.close()


# This function asks the user for contact data in the terminal.
def insert_from_console():
    # Ask for contact name.
    first_name = input("Name: ")

    # Ask for email.
    email = input("Email: ")

    # Ask for birthday. It can be empty.
    birthday = input("Birthday YYYY-MM-DD or empty: ")

    # Ask for group name.
    group_name = input("Group Family/Work/Friend/Other: ")

    # This list stores phone numbers.
    phones = []

    # This loop lets us add many phone numbers.
    while True:
        phone = input("Phone: ")
        phone_type = input("Type home/work/mobile: ")

        # Add one phone and its type to the list.
        phones.append((phone, phone_type))

        # Ask if the user wants to add one more phone.
        more = input("Add another phone? yes/no: ").lower()

        # Stop the loop if answer is not yes.
        if more != "yes":
            break

    # Save contact to the database.
    add_contact(first_name, email, birthday, group_name, phones)


# This function prints rows from the database.
def show_rows(rows):
    # If there are no rows, show message.
    if not rows:
        print("No results")
        return

    # Print every row.
    for row in rows:
        print(row)


# This function shows contacts from one group.
def filter_by_group():
    # Ask for group name.
    group_name = input("Group name: ")

    # Connect to database.
    conn = get_connection()
    cur = conn.cursor()

    # Select contacts where group name is the same.
    cur.execute(
        """
        SELECT c.id, c.first_name, c.email, c.birthday, g.name,
               COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', '), '') AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE g.name ILIKE %s
        GROUP BY c.id, c.first_name, c.email, c.birthday, g.name
        ORDER BY c.first_name
        """,
        (group_name,)
    )

    # Print result.
    show_rows(cur.fetchall())

    # Close connection.
    cur.close()
    conn.close()


# This function searches contacts by email.
def search_by_email():
    # Ask for email text.
    query = input("Email search: ")

    conn = get_connection()
    cur = conn.cursor()

    # ILIKE means search is not strict about big or small letters.
    # % means there can be any text before or after query.
    cur.execute(
        """
        SELECT c.id, c.first_name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE c.email ILIKE %s
        ORDER BY c.first_name
        """,
        (f"%{query}%",)
    )

    show_rows(cur.fetchall())
    cur.close()
    conn.close()


# This function searches by name, email, phone, or group.
def advanced_search():
    # Ask for search text.
    query = input("Search name/email/phone/group: ")

    conn = get_connection()
    cur = conn.cursor()

    # Use SQL function search_contacts from procedures.sql.
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))

    show_rows(cur.fetchall())
    cur.close()
    conn.close()


# This function sorts contacts.
def sort_contacts():
    # Show sort options.
    print("1. Sort by name")
    print("2. Sort by birthday")
    print("3. Sort by date added")
    choice = input("Choose: ")

    # This dictionary keeps safe sort fields.
    allowed = {
        "1": "c.first_name",
        "2": "c.birthday NULLS LAST",
        "3": "c.created_at"
    }

    # If user gives wrong choice, sort by name.
    order_by = allowed.get(choice, "c.first_name")

    conn = get_connection()
    cur = conn.cursor()

    # Get contacts with phones and sort them.
    cur.execute(f"""
        SELECT c.id, c.first_name, c.email, c.birthday, g.name, c.created_at,
               COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', '), '') AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, c.first_name, c.email, c.birthday, g.name, c.created_at
        ORDER BY {order_by}
    """)

    show_rows(cur.fetchall())
    cur.close()
    conn.close()


# This function shows contacts page by page.
def paginated_navigation():
    # Ask how many contacts to show on one page.
    limit = int(input("Page size: "))

    # Offset means where the page starts.
    offset = 0

    # This loop shows pages until user writes quit.
    while True:
        conn = get_connection()
        cur = conn.cursor()

        # Use SQL function get_contacts_paginated.
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
        rows = cur.fetchall()

        # Show current page place.
        print(f"\nPage offset: {offset}")
        show_rows(rows)

        cur.close()
        conn.close()

        # Ask user what to do next.
        command = input("next / prev / quit: ").lower()

        # Go to next page.
        if command == "next":
            offset += limit

        # Go to previous page. Offset cannot be less than 0.
        elif command == "prev":
            offset = max(0, offset - limit)

        # Stop pagination.
        elif command == "quit":
            break

        # Wrong command.
        else:
            print("Unknown command")


# This function saves contacts to a JSON file.
def export_to_json():
    # Ask for file name.
    filename = input("JSON filename: ")

    conn = get_connection()
    cur = conn.cursor()

    # Get all contacts with groups and phones.
    cur.execute("""
        SELECT c.id, c.first_name, c.email, c.birthday, g.name,
               COALESCE(json_agg(json_build_object('phone', p.phone, 'type', p.type))
                        FILTER (WHERE p.id IS NOT NULL), '[]') AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, c.first_name, c.email, c.birthday, g.name
        ORDER BY c.first_name
    """)

    # This list will store all contacts.
    contacts = []

    # Make Python dictionaries from database rows.
    for row in cur.fetchall():
        contacts.append({
            "name": row[1],
            "email": row[2],
            "birthday": str(row[3]) if row[3] else None,
            "group": row[4],
            "phones": row[5]
        })

    # Write contacts to JSON file.
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4, ensure_ascii=False)

    cur.close()
    conn.close()
    print("Export completed")


# This function reads contacts from a JSON file.
def import_from_json():
    # Ask for JSON file name.
    filename = input("JSON filename: ")

    # Open and read JSON file.
    with open(filename, "r", encoding="utf-8") as file:
        contacts = json.load(file)

    conn = get_connection()
    cur = conn.cursor()

    # Add every contact from the JSON file.
    for item in contacts:
        name = item.get("name")

        # Check if this contact already exists.
        cur.execute("SELECT id FROM contacts WHERE first_name = %s", (name,))
        exists = cur.fetchone()

        # If contact exists, ask user what to do.
        if exists:
            action = input(f"{name} already exists. skip/overwrite: ").lower()

            # Skip means do not add this contact.
            if action == "skip":
                continue

            # Overwrite means delete old contact and add new data.
            elif action == "overwrite":
                cur.execute("DELETE FROM contacts WHERE first_name = %s", (name,))

        # Get or create contact group.
        group_id = get_or_create_group(cur, item.get("group"))

        # Add contact to contacts table.
        cur.execute(
            """
            INSERT INTO contacts(first_name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, item.get("email"), item.get("birthday"), group_id)
        )

        # Get new contact id.
        contact_id = cur.fetchone()[0]

        # Add phone numbers for this contact.
        for phone_data in item.get("phones", []):
            cur.execute(
                "INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, phone_data.get("phone"), phone_data.get("type"))
            )

    # Save all changes.
    conn.commit()
    cur.close()
    conn.close()
    print("Import completed")


# This function reads contacts from a CSV file.
def import_from_csv():
    # Ask for CSV file name.
    filename = input("CSV filename: ")

    # Open CSV file.
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Add every row as one contact.
        for row in reader:
            add_contact(
                row["first_name"],
                row.get("email"),
                row.get("birthday"),
                row.get("group"),
                [(row["phone"], row["type"])]
            )


# This function calls SQL procedure add_phone.
def add_phone_procedure():
    # Ask for contact name and new phone.
    name = input("Contact name: ")
    phone = input("New phone: ")
    phone_type = input("Type home/work/mobile: ")

    conn = get_connection()
    cur = conn.cursor()

    # CALL runs a PostgreSQL procedure.
    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()
    print("Procedure add_phone completed")


# This function calls SQL procedure move_to_group.
def move_to_group_procedure():
    # Ask for contact name and new group.
    name = input("Contact name: ")
    group_name = input("New group: ")

    conn = get_connection()
    cur = conn.cursor()

    # Move contact to another group.
    cur.execute("CALL move_to_group(%s, %s)", (name, group_name))

    conn.commit()
    cur.close()
    conn.close()
    print("Procedure move_to_group completed")


# This is the main menu of the program.
def menu():
    # The menu works until the user chooses 0.
    while True:
        # Show all menu options.
        print("\n--- TSIS 1 PHONEBOOK ---")
        print("1. Run schema.sql")
        print("2. Run procedures.sql")
        print("3. Insert contact from console")
        print("4. Filter by group")
        print("5. Search by email")
        print("6. Advanced search")
        print("7. Sort contacts")
        print("8. Paginated navigation")
        print("9. Export to JSON")
        print("10. Import from JSON")
        print("11. Import from CSV")
        print("12. Add phone procedure")
        print("13. Move to group procedure")
        print("0. Exit")

        # Ask user to choose an option.
        choice = input("Choose: ")

        # Run schema file.
        if choice == "1":
            execute_sql_file("schema.sql")

        # Run procedures file.
        elif choice == "2":
            execute_sql_file("procedures.sql")

        # Add contact manually.
        elif choice == "3":
            insert_from_console()

        # Find contacts by group.
        elif choice == "4":
            filter_by_group()

        # Find contacts by email.
        elif choice == "5":
            search_by_email()

        # Find contacts by name, email, phone, or group.
        elif choice == "6":
            advanced_search()

        # Sort contacts.
        elif choice == "7":
            sort_contacts()

        # Show contacts page by page.
        elif choice == "8":
            paginated_navigation()

        # Save contacts to JSON file.
        elif choice == "9":
            export_to_json()

        # Add contacts from JSON file.
        elif choice == "10":
            import_from_json()

        # Add contacts from CSV file.
        elif choice == "11":
            import_from_csv()

        # Add new phone with SQL procedure.
        elif choice == "12":
            add_phone_procedure()

        # Move contact to another group with SQL procedure.
        elif choice == "13":
            move_to_group_procedure()

        # Stop the program.
        elif choice == "0":
            break

        # If choice is wrong, show message.
        else:
            print("Wrong choice")


# This part starts the program.
# It runs only when we start this file directly.
if __name__ == "__main__":
    menu()
