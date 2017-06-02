from os.path    import exists
from os         import makedirs


class archivarIOS():
    def __init__(self, directory_path = './configs'):
        if isinstance(directory_path, str):
            self.dirpath = directory_path
        else:
            self.dirpath = './configs'
        if self.dirpath[-1] != '/':
            self.dirpath += '/'


    def save_config(self, configs):
        if not isinstance(configs, dict):
            return
        config_path = self.dirpath + configs['hostname'] + '/'
        if not exists(config_path):
            makedirs(config_path)
        for config_type in ['running', 'startup']:
            open(config_path + config_type + '.cfg', 'w',).write(configs[config_type])
