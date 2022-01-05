import string
import random
import pandas as pd

# set the number of default characters
DEFAULT_CHARS = 5


# make a default manager class
class Manager:
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

    def random_proxy(self):
        # get a proxy from the dataframe
        proxy = self.proxies_df.sample().to_dict(orient='records')[0]

        # add the proxy type
        proxy['type'] = 'HTTP'
        proxy['mode'] = 'http'

        return proxy

    # make a random name generator
    def random_name(self):
        return f"Random Profile {self.random_string()}"
