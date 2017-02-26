import urllib2
import json

from config import AppConfig


token = None


class RestClient(object):
    """class for interfacing with the MySMDS API"""
    def __init__(self):
        global token
        if token is None:
            self.token = get_token()
            token = self.token
        else:
            self.token = token

    def get_json(self, endpoint_url):
        """Executes a GET request to a JSON API endpoint"""
        app_cfg = AppConfig()

        req = urllib2.Request('%s/api%s' % (app_cfg.api.host, endpoint_url))
        req.add_header('X-JWT', self.token)
        return json.load(urllib2.urlopen(req))

    def post_json(self, endpoint_url, data):
        """Executes a POST requrest to a JSON API endpoint"""
        app_cfg = AppConfig()

        req = urllib2.Request('%s/api%s' % (app_cfg.api.host, endpoint_url))
        req.add_header('X-JWT', self.token)
        return json.load(urllib2.urlopen(req, json.dumps(data)))


def try_connect():
    """Tries to connect to the API"""
    try:
        get_token()
        return True
    except urllib2.URLError or urllib2.HTTPError:
        return False


def get_token():
    cfg = AppConfig()

    data = {
        'id': cfg.dispenser.dispenser_id,
        'authToken': cfg.auth.auth_token
    }

    auth_req = urllib2.Request('%s/api/authenticatedispenser' % cfg.api.host)

    response = json.load(urllib2.urlopen(auth_req, json.dumps(data)))
    return response['token']