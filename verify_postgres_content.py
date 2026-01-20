import psycopg2
import os

# Provided by user (External URL)
DB_URL = "postgresql://nexus_database_78e7_user:wbX57m3xgjCLgwxJsGF7xYlmak0nMoao@dpg-d5njedlactks73che970-a.oregon-postgres.render.com/nexus_database_78e7"

def check_db():
    print(f"Connecting to {DB_URL.split('@')[1]}...")
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # 1. Check Tables
        print("\n--- Tables Check ---")
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        print("Tables found:", [t[0] for t in tables])
        
        # 2. Check Feedback Count
        print("\n--- Feedback Check ---")
        cur.execute("SELECT COUNT(*) FROM feedback;")
        count = cur.fetchone()[0]
        print(f"Total Feedback Rows: {count}")
        
        if count > 0:
            cur.execute("SELECT id, institute_id, timestamp FROM feedback ORDER BY timestamp DESC LIMIT 5;")
            rows = cur.fetchall()
            print("Recent 5 Feedbacks:")
            for r in rows:
                print(f"ID: {r[0]} | Institute: {r[1]} | Time: {r[2]}")

        # 3. Check Institutes
        print("\n--- Institute Check ---")
        cur.execute("SELECT id, name, admin_id, password FROM institutes;")
        inst_rows = cur.fetchall()
        for i in inst_rows:
            print(f"Institute: {i[0]} | Name: {i[1]} | Admin: {i[2]} | Pass: {i[3]}")
    
        conn.close()
        
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    check_db()
