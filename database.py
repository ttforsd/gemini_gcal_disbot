import libsql_experimental as libsql
import os 
from dotenv import load_dotenv

load_dotenv(override=True)

class database:
    def __init__(self):
        self.con = libsql.connect(database=os.getenv("TURSO_DATABASE_URL"), auth_token=os.getenv("TURSO_AUTH_TOKEN"))
        print(os.getenv("TURSO_DATABASE_URL"))
        print(os.getenv("TURSO_AUTH_TOKEN"))
        self.create_entry_table()
        self.create_cal_table()


    def create_entry_table(self): 
        # check if table exists
        

        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS entry_table (entry_id INTEGER PRIMARY KEY AUTOINCREMENT, creation_datetime DATETIME);")
        self.con.commit()
        print("entry_table created")


    def create_cal_table(self): 
        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS cal_table (id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id INTEGER, event_id VARCHAR(255), FOREIGN KEY (entry_id) REFERENCES entry_table(entry_id));")
        self.con.commit()
        # create index for event_id and entry_id in cal_table
        cur.execute("CREATE INDEX IF NOT EXISTS event_id_index ON cal_table (event_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS entry_id_index ON cal_table (entry_id);")
        self.con.commit()
        print("cal_table created")

    def del_tables(self): 
        cur = self.con.cursor()
        cur.execute("DROP TABLE entry_table")
        cur.execute("DROP TABLE cal_table")
        self.con.commit()
        print("tables deleted")

    def delete_entry_by_id(self, entry_id): 
        entry_id = int(entry_id)
        cur = self.con.cursor()
        # get ids of events to delete
        cur.execute("SELECT event_id FROM cal_table WHERE entry_id = ?;", (entry_id,))
        event_ids = cur.fetchall()
        for event_id in event_ids:
            if type(event_id) == tuple: 
                event_id = event_id[0] 
            self.delete_event_by_id(event_id)
        # delete entry
        cur.execute("DELETE FROM entry_table WHERE entry_id = ?;", (entry_id,))
        self.con.commit()
        print(f"entry {entry_id} deleted")
        return True 
        
    def delete_event_by_id(self, event_id): 
        print(event_id, type(event_id))
        cur = self.con.cursor()
        cur.execute("DELETE FROM cal_table WHERE event_id = ?;", (event_id,))
        self.con.commit()
        print(f"event {event_id} deleted")
        return True 
    
    def events_entry(self, events): 
        # create entry and get entry_id
        cur = self.con.cursor()
        cur.execute("INSERT INTO entry_table (creation_datetime) VALUES (datetime('now'));")
        self.con.commit()
        cur.execute("SELECT entry_id FROM entry_table ORDER BY entry_id DESC LIMIT 1;")
        entry_id = cur.fetchone()[0]
        # create event entries
        for event in events: 
            cur.execute("INSERT INTO cal_table (entry_id, event_id) VALUES (?, ?);", (entry_id, event))
            self.con.commit()
            print(f"events {events} added to entry {entry_id}")
        return entry_id
    
    def get_events_by_entry_id(self, entry_id): 
        entry_id = int(entry_id)
        cur = self.con.cursor()
        cur.execute("SELECT event_id FROM cal_table WHERE entry_id = ?;", (entry_id,))
        events = cur.fetchall()
        for event in events: 
            print(event)
            print(type(event))
        return events
        


if __name__ == "__main__":
    db = database()
    db.del_tables()