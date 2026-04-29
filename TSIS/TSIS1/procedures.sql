CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    IF p_contact_name IS NULL OR btrim(p_contact_name) = '' THEN
        RAISE EXCEPTION 'Contact name cannot be empty';
    END IF;

    IF p_phone IS NULL OR p_phone !~ '^\+?[0-9]{10,15}$' THEN
        RAISE EXCEPTION 'Invalid phone format: %', p_phone;
    END IF;

    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type: %. Use home, work or mobile', p_type;
    END IF;

    SELECT id INTO v_contact_id
    FROM contacts
    WHERE LOWER(name) = LOWER(p_contact_name)
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact % does not exist', p_contact_name;
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
BEGIN
    IF p_contact_name IS NULL OR btrim(p_contact_name) = '' THEN
        RAISE EXCEPTION 'Contact name cannot be empty';
    END IF;

    IF p_group_name IS NULL OR btrim(p_group_name) = '' THEN
        RAISE EXCEPTION 'Group name cannot be empty';
    END IF;

    SELECT id INTO v_contact_id
    FROM contacts
    WHERE LOWER(name) = LOWER(p_contact_name)
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact % does not exist', p_contact_name;
    END IF;

    INSERT INTO groups(name)
    VALUES (INITCAP(btrim(p_group_name)))
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM groups
    WHERE LOWER(name) = LOWER(p_group_name)
    LIMIT 1;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;
END;
$$;
