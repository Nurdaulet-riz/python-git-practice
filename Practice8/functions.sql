CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE
);

-- return all records matching a pattern in name or phone
CREATE OR REPLACE FUNCTION search_contacts(pattern_text TEXT)
RETURNS TABLE (
    id INT,
    name VARCHAR,
    phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.phone
    FROM contacts c
    WHERE c.name ILIKE '%' || pattern_text || '%'
       OR c.phone ILIKE '%' || pattern_text || '%'
    ORDER BY c.id;
END;
$$;

-- query contacts with pagination
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE (
    id INT,
    name VARCHAR,
    phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_limit < 0 OR p_offset < 0 THEN
        RAISE EXCEPTION 'LIMIT and OFFSET must be non-negative';
    END IF;

    RETURN QUERY
    SELECT c.id, c.name, c.phone
    FROM contacts c
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$;

-- count all contacts
CREATE OR REPLACE FUNCTION count_contacts()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    total_count INT;
BEGIN
    SELECT COUNT(*) INTO total_count
    FROM contacts;

    RETURN total_count;
END;
$$;