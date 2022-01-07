import string
import random
import pandas as pd

# set the number of default characters
DEFAULT_CHARS = 5


# make a default manager class
class Manager:
    def __init__(self, filename=None, proxy=None):
        if filename and (not proxy):
            # import the proxies from the file
            self.import_proxies(filename)

            # set the own proxy to none
            self.proxy = None
        elif proxy:
            # get the proxy
            self.proxy = proxy

            # set the proxy type
            proxy['type'] = 'HTTP'
            proxy['mode'] = 'http'

    def import_proxies(self, filename):
        # use the filename to open a csv with the proxies
        self.filename = filename

        # open the proxies
        if filename:
            self.proxies_df = pd.read_csv(self.filename).astype(str)
            self.proxies_df.dropna()
        else:
            self.proxies_df = pd.DataFrame({
                'host': [],
                'port': [],
                'username': [],
                'password': [],

            })

    def random_string(self, chars=DEFAULT_CHARS):
        letters = string.ascii_uppercase
        rstring = ''.join(random.choice(letters) for i in range(chars))

        return rstring

    def get_proxy(self):
        if self.proxy:
            return self.proxy
        else:
            # get a proxy from the dataframe
            proxy = self.proxies_df.sample().to_dict(orient='records')[0]
            return proxy

    # make a random name generator
    def random_name(self):
        return f"Random Profile {self.random_string()}"
