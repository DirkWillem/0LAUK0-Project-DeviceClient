import urllib2
import json

from config import AppConfig


class RestClient(object):
    """class for interfacing with the MySMDS API"""
    def __init__(self, token):
        self.token = token

    def get_json(self, endpoint_url):
        """Executes a GET request to a JSON API endpoint"""
        app_cfg = AppConfig()

        req = urllib2.Request(app_cfg.api.host + endpoint_url)
        req.add_header('X-JWT', self.token)
        return json.load(urllib2.urlopen(req))

    def post_json(self, endpoint_url, data):
        """Executes a POST requrest to a JSON API endpoint"""
        app_cfg = AppConfig()

        req = urllib2.Request(app_cfg.api.host + endpoint_url)
        req.add_header('X-JWT', self.token)
        return json.load(urllib2.urlopen(req, json.dumps(data)))

# Retrieve authentication token
cfg = AppConfig()

data = {
    'id': cfg.dispenser.dispenser_id,
    'authToken': cfg.auth.auth_token
}

auth_req = urllib2.Request('%s/authenticatedispenser' % cfg.api.host)
response = json.load(urllib2.urlopen(auth_req, json.dumps(data)))

client = RestClient(response['token'])
