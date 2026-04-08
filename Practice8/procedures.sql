CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE
);

-- working table for invalid rows from bulk insert
CREATE TABLE IF NOT EXISTS invalid_contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(50),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- insert user by name and phone; if user already exists, update phone
CREATE OR REPLACE PROCEDURE upsert_contact(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_name IS NULL OR btrim(p_name) = '' THEN
        RAISE EXCEPTION 'Name cannot be empty';
    END IF;

    IF p_phone IS NULL OR p_phone !~ '^\\+?[0-9]{10,15}$' THEN
        RAISE EXCEPTION 'Invalid phone format: %', p_phone;
    END IF;

    IF EXISTS (SELECT 1 FROM contacts WHERE lower(name) = lower(p_name)) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE lower(name) = lower(p_name);
    ELSE
        INSERT INTO contacts(name, phone)
        VALUES (p_name, p_phone);
    END IF;
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE 'Phone % already exists for another contact', p_phone;
END;
$$;

-- insert many users from arrays; validate phones; use LOOP/IF; save invalid data
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    v_name TEXT;
    v_phone TEXT;
BEGIN
    IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Names and phones arrays must have the same length';
    END IF;

    FOR i IN 1..COALESCE(array_length(p_names, 1), 0) LOOP
        v_name := btrim(p_names[i]);
        v_phone := btrim(p_phones[i]);

        IF v_name IS NULL OR v_name = '' THEN
            INSERT INTO invalid_contacts(name, phone, reason)
            VALUES (p_names[i], p_phones[i], 'Empty name');

        ELSIF v_phone IS NULL OR v_phone !~ '^\\+?[0-9]{10,15}$' THEN
            INSERT INTO invalid_contacts(name, phone, reason)
            VALUES (p_names[i], p_phones[i], 'Invalid phone format');

        ELSE
            BEGIN
                IF EXISTS (SELECT 1 FROM contacts WHERE lower(name) = lower(v_name)) THEN
                    UPDATE contacts
                    SET phone = v_phone
                    WHERE lower(name) = lower(v_name);
                ELSE
                    INSERT INTO contacts(name, phone)
                    VALUES (v_name, v_phone);
                END IF;
            EXCEPTION
                WHEN unique_violation THEN
                    INSERT INTO invalid_contacts(name, phone, reason)
                    VALUES (v_name, v_phone, 'Duplicate phone');
            END;
        END IF;
    END LOOP;
END;
$$;

-- delete by username or phone
CREATE OR REPLACE PROCEDURE delete_contact_proc(p_value TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM contacts
    WHERE lower(name) = lower(p_value)
       OR phone = p_value;
END;
$$;