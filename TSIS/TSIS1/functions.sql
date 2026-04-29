CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id INTEGER,
    contact_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS group_name,
        COALESCE(
            STRING_AGG(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id),
            ''
        ) AS phones
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.name ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR g.name ILIKE '%' || p_query || '%'
       OR EXISTS (
            SELECT 1
            FROM phones p2
            WHERE p2.contact_id = c.id
              AND p2.phone ILIKE '%' || p_query || '%'
       )
    GROUP BY c.id, c.name, c.email, c.birthday, g.name
    ORDER BY c.name;
END;
$$;

CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE (
    contact_id INTEGER,
    contact_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_limit <= 0 OR p_offset < 0 THEN
        RAISE EXCEPTION 'LIMIT must be positive and OFFSET must be non-negative';
    END IF;

    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS group_name,
        COALESCE(
            STRING_AGG(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id),
            ''
        ) AS phones
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$;

CREATE OR REPLACE FUNCTION count_contacts()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    total_count INT;
BEGIN
    SELECT COUNT(*) INTO total_count FROM contacts;
    RETURN total_count;
END;
$$;
