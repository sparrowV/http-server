import json
import requests
import numpy as np

class basicHttp():
    def __init__(self, config):
        with open(config, 'r') as f:
            self.config = json.load(f)
            # print (self.config)

    def run(self):
        tests = [self.test1, self.test2]
        return np.mean([t() for t in tests])
        
    def test1(self):
        """
        Tests for unknown domain.
        """
        vh = self.config['server'][0]
        domain, ip, port, _ = vh.values()
        headers = {'host': 'google.com'}
        url = "http://" + domain + ':' + str(port)
        response = requests.get(url, headers=headers)

        return ((response.status_code == 404)
                 and ('REQUESTED DOMAIN NOT FOUND' in response.text.upper()))

    def test2(self):
        """
        Tests for static files on first domain
        """
        vh1 = self.config['server'][0]
        domain, ip, port, _ = vh1.values()
        url = "http://" + domain + ':' + str(port) + '/index.html'
        response = requests.get(url)

        return ((response.status_code == 200) and (domain in response.text))

    def test3(self):
        """
        Test headers
        """
        vh1 = self.config['server'][0]
        domain, ip, port, _ = vh1.values()
        url = "http://" + domain + ':' + str(port) + '/index.html'
        print(url)
        response = requests.get(url)
        print(response.headers)