import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'lost_and_found.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            item_type TEXT NOT NULL, -- 'found' or 'lost'
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            date_occurred TEXT NOT NULL,
            description TEXT NOT NULL,
            image_url TEXT,
            contact_name TEXT NOT NULL,
            contact_email TEXT NOT NULL,
            contact_phone TEXT,
            secret_pin TEXT NOT NULL,
            status TEXT DEFAULT 'open', -- 'open', 'claim_pending', 'resolved'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Claims table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            claimant_name TEXT NOT NULL,
            claimant_email TEXT NOT NULL,
            claimant_phone TEXT,
            claimant_student_id TEXT,
            proof_description TEXT NOT NULL,
            proof_image_url TEXT,
            status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
            decision_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()

    # Seed initial demo items if table is empty
    cursor.execute('SELECT COUNT(*) FROM items')
    count = cursor.fetchone()[0]
    if count == 0:
        seed_sample_data(conn)

    conn.close()

def seed_sample_data(conn):
    cursor = conn.cursor()
    sample_items = [
        (
            "Apple AirPods Pro (2nd Gen)",
            "found",
            "Electronics",
            "Central Library - 2nd Floor Study Cubicle",
            "2026-10-06",
            "Found an AirPods white charging case with both earbuds inside. Left on desk #42 next to window. Has a small Mario sticker on the back. Claim by confirming what engraving or bluetooth name it has!",
            "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=600&auto=format&fit=crop&q=80",
            "Aarav Sharma",
            "aarav.s@campus.edu",
            "+91 98765 43210",
            "1234",
            "open"
        ),
        (
            "Black Leather Wallet with Student ID",
            "lost",
            "Wallets & IDs",
            "Main Cafeteria / Food Court",
            "2026-10-07",
            "Lost my black Tommy Hilfiger leather wallet around 1:30 PM. Contains university ID card, metro pass, and some cash. Please reach out if you found it!",
            "https://images.unsplash.com/photo-1627123424574-724758594e93?w=600&auto=format&fit=crop&q=80",
            "Priya Patel",
            "priya.p@campus.edu",
            "+91 98111 22334",
            "1234",
            "open"
        ),
        (
            "Casio Scientific Calculator (fx-991EX)",
            "found",
            "Books & Stationery",
            "Engineering Block B - Lecture Hall 101",
            "2026-10-05",
            "Found a Casio fx-991EX ClassWiz calculator after the Physics lecture. Has initials written in marker on the back battery cover. Provide the initials to claim.",
            "https://images.unsplash.com/photo-1594980596870-8aa52a78d8cd?w=600&auto=format&fit=crop&q=80",
            "Rohan Verma",
            "rohan.v@campus.edu",
            "+91 99222 33445",
            "1234",
            "claim_pending"
        ),
        (
            "Hydro Flask Water Bottle (Navy Blue)",
            "found",
            "Personal Items",
            "Sports Complex Gym / Basketball Court",
            "2026-10-04",
            "Navy blue 32oz insulated bottle with 3 stickers (NASA, GitHub, Anime sticker). Found near the bleachers.",
            "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80",
            "Sneha Rao",
            "sneha.r@campus.edu",
            "+91 97333 44556",
            "1234",
            "resolved"
        ),
        (
            "Set of 3 Keys on a Spiderman Lanyard",
            "found",
            "Keys",
            "Hostel 4 Ground Floor Entrance",
            "2026-10-07",
            "Found a set of room & bike keys on a red and blue Spiderman lanyard. Handed over to Hostel Warden desk for safekeeping.",
            "https://images.unsplash.com/photo-1582139329536-e7284fece509?w=600&auto=format&fit=crop&q=80",
            "Vikram Singh",
            "vikram.s@campus.edu",
            "+91 98444 55667",
            "1234",
            "open"
        )
    ]

    cursor.executemany('''
        INSERT INTO items (
            title, item_type, category, location, date_occurred, 
            description, image_url, contact_name, contact_email, 
            contact_phone, secret_pin, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_items)
    conn.commit()

    # Seed one demo claim on the Casio Calculator
    cursor.execute("SELECT id FROM items WHERE title LIKE '%Casio Scientific Calculator%' LIMIT 1")
    calc = cursor.fetchone()
    if calc:
        calc_id = calc[0]
        cursor.execute('''
            INSERT INTO claims (
                item_id, claimant_name, claimant_email, claimant_phone,
                claimant_student_id, proof_description, proof_image_url, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            calc_id,
            "Ananya Sen",
            "ananya.s@campus.edu",
            "+91 98999 11223",
            "STU-2024-8891",
            "The initials on the battery lid are 'A.S.' in blue permanent marker, and the solar cell frame has a tiny scratch on the top-left edge.",
            None,
            "pending"
        ))
        conn.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
