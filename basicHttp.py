import requests
from testsbase import testsbase

class basicHttp(testsbase):
    def __init__(self, config):
        super().__init__(config)

    def run(self, vh=None):
        test_list = [self.test1, self.test2, self.test3, 
                    self.test4, self.test5]
        return super().run(tests=test_list, vh=vh, testfile='index.html')

    def test1(self):
        """
        Tests for unknown domain.
        """
        headers = {'host': 'google.com'}
        response = requests.get(self.url, headers=headers)
        return ((response.status_code == 404)
                 and ('REQUESTED DOMAIN NOT FOUND' in response.text.upper()))

    def test2(self):
        """
        Tests for static files
        """
        response = requests.get(self.url)
        return ((response.status_code == 200) and (self.domain in response.text))

    def test3(self):
        """
        Tests supported headers
        """
        response = requests.get(self.url)    
        return all (h in response.headers for h in ['server', 'date', 'content-length', 
                                                    'content-type', 'etag'])

    def test4(self):
        """
        Tests content-length
        """
        content_length = int(requests.head(self.url).headers['content-length'])
        response = requests.get(self.url)
        return content_length == len(response.text)

    def test5(self):
        """
        Tests HEAD method support
        """
        response = requests.head(self.url)
        return all (h in response.headers for h in ['server', 'date', 'content-length', 
                                                    'content-type', 'etag'])

    def test6(self):
        """
        Test for etag 
        """
        response = requests.get(self.url)
        etag = response.headers['etag']
        response = requests.get(self.url, headers={'If-None-Match': etag})
        return response.status_code == 304
