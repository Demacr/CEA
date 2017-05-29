from db             import Database
from devicehandler  import DeviceHandler


dtype = 'cisco_ios'
host = '10.0.0.1'
user = 'username'
pwrd = 'password'
port = 22
dbse = 'db.sqlite3'


def main():
    db = Database(dbse)
    dh = DeviceHandler(dtype, host, port, user, pwrd)
    dh.run_start_equality()


if __name__ == '__main__':
    main()