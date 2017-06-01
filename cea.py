from db             import Database


dbse = 'db.sqlite3'


def main():
    db = Database(dbse)
    devices = db.get_device_driver('SW_IT', filter_type='in')
    for device in devices:
        device.open()
        print(device.hostname, device.cli(['show ip int br']))


if __name__ == '__main__':
    main()