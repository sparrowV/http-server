import json
from numpy import mean

class testsbase():
    """
    Range header tests
    """
    def __init__(self, config):
        with open(config, 'r') as f:
            self.config = json.load(f)

    def run(self, tests=None, vh=None, testfile='index.html'):
        if vh is None:
            vh = self.config['server'][0]

        self.domain = vh['vhost']
        self.ip = vh['ip']
        self.port = vh['port']
        self.docroot = vh['documentroot']
        self.url = "http://" + self.domain + ':' + str(self.port) + '/' + testfile

        score = []
        for t in tests:
            try:
                print("Running {} {}: ".format(type(self).__name__, t.__name__, t.__doc__), end='')
                result = t()
                score.append(result)
                print(result)
            except Exception as err:
                print("test crashed: {}".format(err))

        return mean(score)
