CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO groups(name)
VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    birthday DATE,
    group_id INTEGER REFERENCES groups(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE contacts ADD COLUMN IF NOT EXISTS email VARCHAR(100);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS birthday DATE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS group_id INTEGER;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'contacts_group_id_fkey'
          AND table_name = 'contacts'
    ) THEN
        ALTER TABLE contacts
        ADD CONSTRAINT contacts_group_id_fkey
        FOREIGN KEY (group_id) REFERENCES groups(id);
    END IF;
END;
$$;

CREATE UNIQUE INDEX IF NOT EXISTS contacts_name_lower_unique
ON contacts (LOWER(name));

CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL UNIQUE,
    type VARCHAR(10) NOT NULL CHECK (type IN ('home', 'work', 'mobile'))
);

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'contacts'
          AND column_name = 'phone'
    ) THEN
        INSERT INTO phones(contact_id, phone, type)
        SELECT id, phone, 'mobile'
        FROM contacts
        WHERE phone IS NOT NULL
        ON CONFLICT (phone) DO NOTHING;

        ALTER TABLE contacts DROP COLUMN phone;
    END IF;
END;
$$;
