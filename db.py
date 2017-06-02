import sqlite3


from napalm_ios import IOSDriver


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

    def get_device_driver(self, hostname = None, ip_address = None, device_type = None, filter_type = 'exact'):
        first_percent = ''
        second_percent = ''
        result = []
        if filter_type not in ['exact', 'in', 'begin_with', 'end_with']:
            filter_type = 'exact'
        else:
            if filter_type in ['in', 'begin_with']:
                first_percent = '%'
            if filter_type in ['in', 'end_with']:
                second_percent = '%'
        if hostname is None and ip_address is None and device_type is None:
            return result
        filters = dict((k,v) for k,v in {'hostname': hostname, 'ipaddr': ip_address, 'device_type': device_type}.items()
                       if v is not None)
        conn = sqlite3.connect(self.db)
        curs = conn.cursor()
        curs.execute('''
            SELECT device_type, hostname, ipaddr, port, username, password, secret 
            FROM devices INNER JOIN profiles ON devices.id_profile = profiles.id 
            WHERE ''' + ' AND '.
                     join(["{} LIKE '{}{}{}'".format(k, first_percent, v, second_percent) for k,v in filters.items()]))
        sql_result = curs.fetchall()
        if sql_result is None:
            return result
        for row in sql_result:
            if row[0] == 'cisco_ios':
                result.append(IOSDriver(row[2], row[4], row[5], optional_args={'secret': row[6]}))
        conn.close()
        return result