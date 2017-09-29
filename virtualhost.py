import json
import requests
import numpy as np

class virtualhost():
    """
        Virtual hosting testing class
    """
    def __init__(self, config):
        with open(config, 'r') as f:
            self.config = json.load(f)
            # print (self.config)

    def run(self):
        tests = [self.test1]
        return np.mean([t() for t in tests])

    def test1(self):
        for vh in self.config['server']:
            domain = vh['vhost']
            ip = vh['ip']
            port = vh['port']
            print(domain, ip, port)
            print("http://" + domain + ':' + str(port))
            response = requests.get("http://" + domain + ':' + str(port))
            print(response.headers)
            print(response.text)
        return 0

    