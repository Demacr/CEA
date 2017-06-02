class archivarIOS():
    def __init__(self, directory_path = './configs'):
        if isinstance(directory_path, str):
            self.dirpath = directory_path
        else:
            self.dirpath = './configs'

    def save_config(self, configs):
        if not isinstance(configs, dict):
            return
