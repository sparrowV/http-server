import requests
from hashlib import sha256
from testsbase import testsbase

class rangeheader(testsbase):
    """
    Range header tests
    """
    def __init__(self, config):
        super().__init__(config)

    def run(self, vh=None):
        test_list = [self.test1, self.test2, self.test3, self.test4]
        return super().run(tests=test_list, vh=None, testfile='random.file')

    def test1(self):
        """
        check ACCEPT-RANGES header
        """
        response = requests.head(self.url)
        return 'ACCEPT-RANGES' in response.headers

    def test2(self):
        """
        check ACCEPT-RANGES header's value
        """
        response = requests.head(self.url)
        return response.headers['ACCEPT-RANGES'].lower() == 'bytes'

    def test3(self):
        """
        check range 1000-1999
        """
        return self.check_range(offset=1000, length=1000)

    def test4(self):
        """
        check range 0-
        """
        return self.check_range(offset=1000, length=0)

    def check_range(self, offset=0, length=0):
        h = sha256()
        m = sha256()
        with open("example1/random.file", "rb") as f:
            f.seek(offset, 0)
            if length:
                data = f.read(length)
                range_bytes = "bytes={}-{}".format(offset, offset+length-1)
            else:
                data = f.read()
                range_bytes = "bytes={}-".format(offset)
            h.update(data)

        response = requests.get(self.url, headers={"Range": range_bytes})
        m.update(response.content)

        return m.digest() == h.digest()

