import sqlite3

DBVERSION = 1

class Database():
    def __init__(self, db):
        self.db = db
        self.__check_database()


    def __check_database(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name FROM sqlite_master WHERE type='table' AND name='info'
        ''')
        if cursor.fetchone() is None:
            self.__create_tables()
            print('Create tables')
        else:
            cursor.execute('''
                SELECT dbversion FROM info
            ''')
            readversion = int(cursor.fetchone()[0])
            if readversion != DBVERSION:
                #TODO make migration
                print('Need migration')
                pass
        conn.commit()
        conn.close()


    def __create_tables(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE info (
                dbversion INTEGER NOT NULL
            )
        ''')

        cursor.execute('''
            INSERT INTO info (dbversion)
            VALUES (?)
        ''', (DBVERSION,))

        cursor.execute('''
            CREATE TABLE profiles (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NULL,
                secret TEXT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE devices (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                device_type TEXT NOT NULL,
                hostname TEXT NULL,
                ipaddr TEXT NOT NULL,
                port INTEGER DEFAULT 22,
                id_profile INTEGER NOT NULL,
                FOREIGN KEY (id_profile) REFERENCES profiles(id)
                )
        ''')

        conn.commit()
        conn.close()


    def add_profile(self, profile_name, username, password = None, secret = None):
        conn = sqlite3.connect(self.db)
        curs = conn.cursor()
        curs.execute('''
            INSERT INTO profiles (name, username, password, secret)
            SELECT ?,?,?,? WHERE NOT EXISTS 
            (SELECT 1 FROM profiles WHERE name=? AND username=? AND password=? AND secret=?)            
        ''', (profile_name, username, password, secret, profile_name, username, password, secret))
        conn.commit()
        conn.close()


    def add_device(self, device_type, hostname, ip_address, port, profile):
        conn = sqlite3.connect(self.db)
        curs = conn.cursor()
        if isinstance(profile,(int,)):
            curs.execute('''
                INSERT INTO devices (device_type, hostname, ipaddr, port, id_profile)
                SELECT ?,?,?,?,? WHERE NOT EXISTS 
                (SELECT 1 FROM devices WHERE device_type=? AND hostname=? AND ipaddr=? AND port=? AND id_profile=?)
            ''', (device_type, hostname, ip_address, port, profile, device_type, hostname, ip_address, port, profile))
        elif isinstance(profile, (str,)):
            curs.execute('''
                INSERT INTO devices (device_type, hostname, ipaddr, port, id_profile)
                SELECT ?,?,?,?,(SELECT id FROM profiles WHERE name = ?) WHERE NOT EXISTS 
                (SELECT 1 FROM devices WHERE device_type=? AND hostname=? AND ipaddr=? AND port=? AND id_profile=
                    (SELECT id from profiles WHERE name = ?))
            ''', (device_type, hostname, ip_address, port, profile, device_type, hostname, ip_address, port, profile))
        conn.commit()
        conn.close()