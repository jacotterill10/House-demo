from database import init_db, get_connection

LISTINGS = [
    (1, "2-bed terrace in Wakefield City Centre", 184950, "City Centre", 2, 1, "House", 11, 760, 53.6832, -1.4976, "#"),
    (2, "3-bed semi in Outwood", 239500, "Outwood", 3, 2, "Semi-detached", 18, 1010, 53.7150, -1.5070, "#"),
    (3, "1-bed flat near Wakefield Westgate", 122000, "City Centre", 1, 1, "Flat", 7, 480, 53.6802, -1.5068, "#"),
    (4, "4-bed detached in Sandal", 359950, "Sandal", 4, 2, "Detached", 16, 1480, 53.6649, -1.4860, "#"),
    (5, "2-bed semi in Horbury", 198000, "Horbury", 2, 1, "Semi-detached", 20, 820, 53.6602, -1.5608, "#"),
    (6, "3-bed family home in Stanley", 214995, "Stanley", 3, 1, "House", 15, 980, 53.7015, -1.4557, "#"),
    (7, "2-bed flat in Alverthorpe", 149950, "Alverthorpe", 2, 1, "Flat", 14, 610, 53.6927, -1.5340, "#"),
    (8, "3-bed detached in Sandal", 289950, "Sandal", 3, 2, "Detached", 17, 1210, 53.6685, -1.4893, "#"),
]

def seed():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM listings")

    cursor.executemany("""
    INSERT INTO listings (
        id, title, price, area, beds, baths, type, commute, size, lat, lng, url
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, LISTINGS)

    conn.commit()
    conn.close()
    print("Database seeded.")

if __name__ == "__main__":
    seed()