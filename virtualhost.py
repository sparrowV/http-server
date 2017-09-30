from numpy import mean
from basicHttp import basicHttp

class virtualhost(basicHttp):
    """
        Virtual hosting testing class
    """
    def __init__(self, config):
        super().__init__(config)

    def run(self):
        r = []
        for vh in self.config['server']:
            r.append(super().run(vh))
        return mean(r)