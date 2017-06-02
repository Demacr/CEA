from db             import Database
from archivarIOS    import archivarIOS


dbse = 'db.sqlite3'


def main():
    db = Database(dbse)
    arch = archivarIOS()
    devices = db.get_device_driver('SW_IT', filter_type='in')
    for device in devices:
        device.open()
        dev_configs = device.get_config('all')
        arch.save_config({**dev_configs, 'hostname': device.hostname})


if __name__ == '__main__':
    main()