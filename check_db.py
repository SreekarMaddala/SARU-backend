import sqlite3
conn = sqlite3.connect('saru.db')
cur = conn.cursor()

print("=== Products schema ===")
for row in cur.execute("SELECT sql FROM sqlite_master WHERE name='products'"):
    print(row[0])

print("\n=== Feedback schema ===")
for row in cur.execute("SELECT sql FROM sqlite_master WHERE name='feedback'"):
    print(row[0])

print("\n=== PRAGMA foreign_keys ===")
print(cur.execute("PRAGMA foreign_keys;").fetchone()[0])

print("\n=== Products ===")
for row in cur.execute("SELECT id, name, company_id FROM products"):
    print(row)

print("\n=== Feedback with product_id ===")
for row in cur.execute("SELECT id, product_id FROM feedback WHERE product_id IS NOT NULL LIMIT 10"):
    print(row)

conn.close()

