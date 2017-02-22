import urllib2
import json

from config import AppConfig

api_url = 'http://localhost:5000/api'


class RestClient(object):
    """class for interfacing with the MySMDS API"""
    def __init__(self, token):
        self.token = token

    def get_json(self, endpoint_url):
        """Executes a GET request to a JSON API endpoint"""
        req = urllib2.Request(api_url + endpoint_url)
        req.add_header('X-JWT', self.token)
        return json.load(urllib2.urlopen(req))

# Retrieve authentication token
cfg = AppConfig()

data = {
    'id': cfg.dispenser.dispenser_id,
    'authToken': cfg.auth.auth_token
}

auth_req = urllib2.Request('%s/authenticatedispenser' % api_url)
response = json.load(urllib2.urlopen(auth_req, json.dumps(data)))

client = RestClient(response['token'])
