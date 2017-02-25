import ConfigParser


class AppConfig(object):
    """Contains the application configuration data"""

    class DbConfig(object):
        def __init__(self, host, user, password, database):
            self.host = host
            self.user = user
            self.password = password
            self.database = database

    class AuthConfig(object):
        def __init__(self, auth_token):
            self.auth_token = auth_token

    class DispenserConfig(object):
        def __init__(self, dispenser_id, patient_id):
            self.dispenser_id = dispenser_id
            self.patient_id = patient_id

    class ApiConfig(object):
        def __init__(self, host):
            self.host = host

    class DisplayConfig(object):
        def __init__(self, width, height):
            self.width = width
            self.height = height

    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('./config.cfg')

        self.db = self.DbConfig(
            config.get('database', 'host'),
            config.get('database', 'user'),
            config.get('database', 'password'),
            config.get('database', 'database'))

        self.auth = self.AuthConfig(
            config.get('auth', 'token'))

        self.dispenser = self.DispenserConfig(
            config.getint('dispenser', 'dispenser_id'),
            config.getint('dispenser', 'patient_id'))

        self.api = self.ApiConfig(config.get('api', 'host'))

        self.display = self.DisplayConfig(
            config.getint('display', 'width'),
            config.getint('display', 'height'))
