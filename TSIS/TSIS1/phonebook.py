import csv
import json
from datetime import datetime
from connect import connect

VALID_PHONE_TYPES = {"home", "work", "mobile"}
VALID_SORTS = {
    "name": "c.name",
    "birthday": "c.birthday",
    "date": "c.created_at",
}


def parse_date(date_str):
    """Convert text to date object. Accepts YYYY-MM-DD or empty value."""
    if not date_str:
        return None
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_or_create_group(cur, group_name):
    """Return group id. If group does not exist, create it."""
    if not group_name:
        group_name = "Other"

    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,),
    )
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    return row[0] if row else None


# -------------------------------
# Contact creation / update logic
# -------------------------------
def create_contact_with_details(name, email, birthday, group_name, phones):
    """Insert a new contact with all extended fields and multiple phones."""
    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        group_id = get_or_create_group(cur, group_name)

        cur.execute(
            """
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, email, birthday, group_id),
        )
        contact_id = cur.fetchone()[0]

        for phone, phone_type in phones:
            if phone_type not in VALID_PHONE_TYPES:
                print(f"Skipped phone {phone}: invalid type '{phone_type}'")
                continue
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))

        conn.commit()
        print("Contact added successfully.")
    except Exception as e:
        conn.rollback()
        print("Error while adding contact:", e)
    finally:
        cur.close()
        conn.close()



def overwrite_contact(name, email, birthday, group_name, phones): #dlya exist contact
    """Overwrite an existing contact by name."""
    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        group_id = get_or_create_group(cur, group_name)

        cur.execute(
            """
            UPDATE contacts
            SET email = %s,
                birthday = %s,
                group_id = %s
            WHERE name = %s
            RETURNING id
            """,
            (email, birthday, group_id, name),
        )
        row = cur.fetchone()

        if not row:
            conn.rollback()
            print("Contact not found.")
            return

        contact_id = row[0]
        cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))

        for phone, phone_type in phones:
            if phone_type not in VALID_PHONE_TYPES:
                print(f"Skipped phone {phone}: invalid type '{phone_type}'")
                continue
            cur.execute(
                "INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, phone, phone_type),
            )

        conn.commit()
        print("Contact overwritten successfully.")
    except Exception as e:
        conn.rollback()
        print("Error while overwriting contact:", e)
    finally:
        cur.close()
        conn.close()



def contact_exists(cur, name): #Proverka exist contact
    """Check whether a contact with this name already exists."""
    cur.execute("SELECT 1 FROM contacts WHERE name = %s", (name,)) 
    return cur.fetchone() is not None



def collect_phones_from_console(): #dlya napisanya mnogo nomerov
    """Ask user for multiple phone numbers until they stop."""
    phones = []
    while True:
        phone = input("Enter phone (leave empty to stop): ").strip()
        if not phone:
            break
        phone_type = input("Type [home/work/mobile]: ").strip().lower()
        if phone_type not in VALID_PHONE_TYPES:
            print("Invalid type. Allowed: home, work, mobile")
            continue
        phones.append((phone, phone_type))
    return phones



def add_contact_extended(): #menu dlya add contact
    """Console input for the new extended contact model."""
    name = input("Enter name: ").strip()
    email = input("Enter email: ").strip() or None
    birthday_input = input("Enter birthday (YYYY-MM-DD or empty): ").strip()
    group_name = input("Enter group [Family/Work/Friend/Other]: ").strip() or "Other"

    try:
        birthday = parse_date(birthday_input) if birthday_input else None
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD")
        return

    phones = collect_phones_from_console()
    if not phones:
        print("At least one phone is required.")
        return

    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        exists = contact_exists(cur, name)
    finally:
        cur.close()
        conn.close()

    if exists:
        action = input("Contact already exists. Choose [skip/overwrite]: ").strip().lower()
        if action == "overwrite":
            overwrite_contact(name, email, birthday, group_name, phones)
        else:
            print("Skipped.")
    else:
        create_contact_with_details(name, email, birthday, group_name, phones)


# -------------------------------
# Search / filter / sort / pages
# -------------------------------
def print_contacts(rows):
    """Pretty print contacts returned from SQL queries."""
    if not rows:
        print("No contacts found.")
        return

    for row in rows:
        print("-" * 60)
        print(f"Name      : {row[1]}")
        print(f"Email     : {row[2] or '-'}")
        print(f"Birthday  : {row[3] or '-'}")
        print(f"Group     : {row[4] or '-'}")
        print(f"Created   : {row[5]}")
        print(f"Phones    : {row[6] or '-'}")
    print("-" * 60)



def search_all_fields(): #search po vsem data like name , mail or phone
    """Use the new DB function search_contacts(p_query)."""
    query = input("Enter search text: ").strip()

    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
        print_contacts(rows)
    except Exception as e:
        print("Search error:", e)
    finally:
        cur.close()
        conn.close()



def search_by_email(): #poisk po email
    """Search contacts by partial email match."""
    query = input("Enter part of email: ").strip()

    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                c.id,
                c.name,
                c.email,
                c.birthday,
                g.name,
                c.created_at,
                COALESCE(STRING_AGG(ph.type || ': ' || ph.phone, ', ' ORDER BY ph.type, ph.phone), '')
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            WHERE COALESCE(c.email, '') ILIKE %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
            ORDER BY c.name
            """,
            (f"%{query}%",),
        )
        rows = cur.fetchall()
        print_contacts(rows)
    except Exception as e:
        print("Email search error:", e)
    finally:
        cur.close()
        conn.close()



def filter_by_group(): 
    """Show contacts that belong to one selected group."""
    group_name = input("Enter group name: ").strip()

    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                c.id,
                c.name,
                c.email,
                c.birthday,
                g.name,
                c.created_at,
                COALESCE(STRING_AGG(ph.type || ': ' || ph.phone, ', ' ORDER BY ph.type, ph.phone), '')
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            WHERE g.name = %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
            ORDER BY c.name
            """,
            (group_name,),
        )
        rows = cur.fetchall()
        print_contacts(rows)
    except Exception as e:
        print("Filter error:", e)
    finally:
        cur.close()
        conn.close()



def sort_contacts():
    """Sort contacts by name, birthday, or date added."""
    sort_key = input("Sort by [name/birthday/date]: ").strip().lower()
    if sort_key not in VALID_SORTS:
        print("Invalid sort option.")
        return

    order_by = VALID_SORTS[sort_key]

    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT
                c.id,
                c.name,
                c.email,
                c.birthday,
                g.name,
                c.created_at,
                COALESCE(STRING_AGG(ph.type || ': ' || ph.phone, ', ' ORDER BY ph.type, ph.phone), '')
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
            ORDER BY {order_by} NULLS LAST
            """
        )
        rows = cur.fetchall()
        print_contacts(rows)
    except Exception as e:
        print("Sort error:", e)
    finally:
        cur.close()
        conn.close()



def paginate_navigation():
    """Console page navigation using next / prev / quit."""
    try:
        limit = int(input("Enter page size: ").strip())
    except ValueError:
        print("Limit must be an integer.")
        return

    offset = 0
    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        while True:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.name,
                    c.email,
                    c.birthday,
                    g.name,
                    c.created_at,
                    COALESCE(STRING_AGG(ph.type || ': ' || ph.phone, ', ' ORDER BY ph.type, ph.phone), '')
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones ph ON ph.contact_id = c.id
                GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
                ORDER BY c.name
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cur.fetchall()

            print(f"\nPage offset = {offset}")
            print_contacts(rows)

            command = input("Command [next/prev/quit]: ").strip().lower()
            if command == "next":
                if rows:
                    offset += limit
                else:
                    print("No more pages.")
            elif command == "prev":
                offset = max(0, offset - limit)
            elif command == "quit":
                break
            else:
                print("Unknown command.")
    except Exception as e:
        print("Pagination error:", e)
    finally:
        cur.close()
        conn.close()


# -------------------------------
# Import / Export
# -------------------------------
def export_to_json():
    """Export all contacts with phones and group to a JSON file."""
    filename = input("Enter JSON filename to export: ").strip() or "contacts_export.json"

    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                c.id,
                c.name,
                c.email,
                c.birthday,
                g.name,
                c.created_at
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY c.name
            """
        )
        contacts = cur.fetchall()

        result = []
        for contact in contacts:
            contact_id, name, email, birthday, group_name, created_at = contact
            cur.execute(
                "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY type, phone",
                (contact_id,),
            )
            phones = [{"phone": p, "type": t} for p, t in cur.fetchall()]
            result.append(
                {
                    "name": name,
                    "email": email,
                    "birthday": str(birthday) if birthday else None,
                    "group": group_name,
                    "created_at": str(created_at),
                    "phones": phones,
                }
            )

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        print(f"Exported to {filename}")
    except Exception as e:
        print("Export error:", e)
    finally:
        cur.close()
        conn.close()



def import_from_json():
    """Import contacts from JSON and ask skip/overwrite on duplicates by name."""
    filename = input("Enter JSON filename to import: ").strip()

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("Cannot read JSON:", e)
        return

    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()

        for item in data:
            name = item.get("name")
            email = item.get("email")
            birthday = parse_date(item.get("birthday")) if item.get("birthday") else None
            group_name = item.get("group") or "Other"
            phones = []

            for ph in item.get("phones", []):
                p = ph.get("phone")
                t = ph.get("type", "mobile").lower()
                if p and t in VALID_PHONE_TYPES:
                    phones.append((p, t))

            cur.execute("SELECT 1 FROM contacts WHERE name = %s", (name,))
            exists = cur.fetchone() is not None

            if exists:
                action = input(f"Duplicate contact '{name}'. Choose [skip/overwrite]: ").strip().lower()
                if action == "overwrite":
                    overwrite_contact(name, email, birthday, group_name, phones)
                else:
                    print(f"Skipped {name}")
            else:
                create_contact_with_details(name, email, birthday, group_name, phones)

        print("JSON import finished.")
    except Exception as e:
        print("Import error:", e)
    finally:
        cur.close()
        conn.close()



def import_from_csv():
    """Extended CSV import.

    Expected columns:
    name,email,birthday,group,phone,phone_type
    """
    filename = input("Enter CSV filename: ").strip()

    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print("Cannot read CSV:", e)
        return

    grouped = {}
    for row in rows:
        name = (row.get("name") or "").strip()
        if not name:
            continue

        grouped.setdefault(
            name,
            {
                "email": (row.get("email") or "").strip() or None,
                "birthday": (row.get("birthday") or "").strip() or None,
                "group": (row.get("group") or "Other").strip() or "Other",
                "phones": [],
            },
        )

        phone = (row.get("phone") or "").strip()
        phone_type = (row.get("phone_type") or "mobile").strip().lower()
        if phone:
            grouped[name]["phones"].append((phone, phone_type))

    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        for name, info in grouped.items():
            cur.execute("SELECT 1 FROM contacts WHERE name = %s", (name,))
            exists = cur.fetchone() is not None

            birthday = parse_date(info["birthday"]) if info["birthday"] else None
            if exists:
                action = input(f"Duplicate contact '{name}'. Choose [skip/overwrite]: ").strip().lower()
                if action == "overwrite":
                    overwrite_contact(name, info["email"], birthday, info["group"], info["phones"])
                else:
                    print(f"Skipped {name}")
            else:
                create_contact_with_details(name, info["email"], birthday, info["group"], info["phones"])

        print("CSV import finished.")
    except Exception as e:
        print("CSV import error:", e)
    finally:
        cur.close()
        conn.close()


# -------------------------------
# Extra actions for new procedures
# -------------------------------
def add_new_phone_to_contact():
    """Call DB procedure add_phone."""
    name = input("Enter contact name: ").strip()
    phone = input("Enter phone: ").strip()
    phone_type = input("Enter type [home/work/mobile]: ").strip().lower()

    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()
        print("Phone added.")
    except Exception as e:
        conn.rollback()
        print("Add phone error:", e)
    finally:
        cur.close()
        conn.close()



def move_contact_to_group():
    """Call DB procedure move_to_group."""
    name = input("Enter contact name: ").strip()
    group_name = input("Enter new group name: ").strip()

    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        conn.commit()
        print("Contact moved to group.")
    except Exception as e:
        conn.rollback()
        print("Move error:", e)
    finally:
        cur.close()
        conn.close()


# -------------------------------
# Main menu
# -------------------------------
def main():
    while True:
        print("\n========== EXTENDED PHONEBOOK ==========")
        print("1. Add contact with extended fields")
        print("2. Search across all fields")
        print("3. Search by email")
        print("4. Filter by group")
        print("5. Sort contacts")
        print("6. Paginated navigation")
        print("7. Export to JSON")
        print("8. Import from JSON")
        print("9. Import from CSV")
        print("10. Add one more phone to contact")
        print("11. Move contact to another group")
        print("0. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            add_contact_extended()
        elif choice == "2":
            search_all_fields()
        elif choice == "3":
            search_by_email()
        elif choice == "4":
            filter_by_group()
        elif choice == "5":
            sort_contacts()
        elif choice == "6":
            paginate_navigation()
        elif choice == "7":
            export_to_json()
        elif choice == "8":
            import_from_json()
        elif choice == "9":
            import_from_csv()
        elif choice == "10":
            add_new_phone_to_contact()
        elif choice == "11":
            move_contact_to_group()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()