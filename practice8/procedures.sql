CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_name) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE first_name = p_name;
    ELSE
        INSERT INTO phonebook(first_name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE first_name = p_value OR phone = p_value;
END;
$$;


CREATE OR REPLACE FUNCTION bulk_insert_contacts(
    p_names TEXT[],
    p_phones TEXT[]
)
RETURNS TEXT[]
LANGUAGE plpgsql
AS $$
DECLARE
    i INTEGER;
    invalid_data TEXT[] := '{}';
BEGIN
    FOR i IN 1..array_length(p_names, 1) LOOP
        IF p_phones[i] ~ '^[0-9]{10,15}$' THEN
            IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_names[i]) THEN
                UPDATE phonebook
                SET phone = p_phones[i]
                WHERE first_name = p_names[i];
            ELSE
                INSERT INTO phonebook(first_name, phone)
                VALUES (p_names[i], p_phones[i]);
            END IF;
        ELSE
            invalid_data := array_append(
                invalid_data,
                p_names[i] || ' - ' || p_phones[i]
            );
        END IF;
    END LOOP;

    RETURN invalid_data;
END;
$$;