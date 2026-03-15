"""
Database module.
A02: Stores PII (SSN, credit card) and secrets in plaintext.
A02: Passwords hashed with MD5 (no salt).
"""
import hashlib
import sqlite3

DATABASE_FILE = "vulnerable.db"


def get_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT UNIQUE NOT NULL,
            password        TEXT NOT NULL,   -- A02: MD5, no salt
            email           TEXT,
            role            TEXT DEFAULT 'user',
            ssn             TEXT,            -- A02: PII stored in plaintext
            credit_card     TEXT,            -- A02: PII stored in plaintext
            api_key         TEXT             -- A02: Secret stored in plaintext
        );

        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            description TEXT,               -- A03: stored XSS vector
            price       REAL,
            owner_id    INTEGER,
            category    TEXT
        );

        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            product_id  INTEGER,
            quantity    INTEGER,
            total       REAL
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            action    TEXT,
            user_id   INTEGER,
            timestamp TEXT,
            details   TEXT   -- A09: plaintext passwords end up here
        );
    """)

    # A07: Default credentials admin/admin seeded into the database
    admin_pw = hashlib.md5(b"admin").hexdigest()       # noqa: S324
    user_pw  = hashlib.md5(b"password123").hexdigest() # noqa: S324

    cur.execute(
        "INSERT OR IGNORE INTO users (username,password,email,role,ssn,credit_card,api_key) VALUES (?,?,?,?,?,?,?)",
        ("admin", admin_pw, "admin@corp.internal", "admin",
         "123-45-6789", "4111111111111111", "sk-prod-HARDCODED1234567890"),
    )
    cur.execute(
        "INSERT OR IGNORE INTO users (username,password,email,role,ssn,credit_card,api_key) VALUES (?,?,?,?,?,?,?)",
        ("alice", user_pw, "alice@example.com", "user",
         "987-65-4321", "5500005555555559", "sk-user-abcdef1234567890"),
    )

    cur.executemany(
        "INSERT OR IGNORE INTO products (id,name,description,price,owner_id,category) VALUES (?,?,?,?,?,?)",
        [
            (1, "Laptop",  "High-performance laptop",  999.99, 1, "electronics"),
            (2, "Phone",   "Latest smartphone",        699.99, 1, "electronics"),
            (3, "Book",    "Python security guide",     29.99, 2, "books"),
        ],
    )

    conn.commit()
    conn.close()
