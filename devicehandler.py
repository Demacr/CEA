import netmiko


RunningConfig = 'running-config'
StartupConfig = 'startup-config'


class DeviceHandler():
    def __init__(self, device_type, hostname, port, username, password):
        self.device_info = {
            'device_type': device_type,
            'ip': hostname,
            'username': username,
            'password': password,
            'port': port
        }


    def __cisco_ios_process_configs_diff(self, diff):
        cert_dict = {}
        splitted_diff = diff.split('\n')
        index = -1
        while index < len(splitted_diff)-1:
            index += 1
            line = splitted_diff[index]
            if len(line) == 0 or line[0] == '!':
                continue
            if line[0] == '+' or line[0] == '-':
                return False
            if line.startswith('crypto pki certificate chain '):
                cert_name = line.replace('crypto pki certificate chain ', '')
                cert_dict[cert_name] = {}
                index += 1
                line = splitted_diff[index]
                if line.startswith('certificate self-signed ', 2):
                    line = line[2:].replace('certificate self-signed ', '')
                    if len(line) < 3:
                        #TODO parse the certificate
                        pass
                    else:
                        cert_file = line[3:]
                        cert_dict[cert_name]['file'] = cert_file
        pass


    def execute(self, command):
        client = netmiko.ConnectHandler(**self.device_info)
        if isinstance(command, str):
            return client.send_command(command)
        elif isinstance(command, list):
            return client.send_config_set(command)


    def get_config(self, type=RunningConfig):
        if self.device_info['device_type'] == 'cisco_ios':
            if type != RunningConfig or type != StartupConfig:
                type = RunningConfig
            client = netmiko.ConnectHandler(**self.device_info)
            open('configs/{0}.cfg'.format(self.device_info['ip']),'w')\
                .write(client.send_command('show {0}'.format(type)))


    def run_start_equality(self, write_memory=False):
        if self.device_info['device_type'] == 'cisco_ios':
            client = netmiko.ConnectHandler(**self.device_info)
            diff = client.send_command('show archive config differences')
            result = self.__cisco_ios_process_configs_diff(diff)
            if not result and write_memory:
                return client.send_command_expect('write memory')
            return result