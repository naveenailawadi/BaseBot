from core.BaseBot.platforms.Managers import Manager
from json.decoder import JSONDecodeError
from selenium import webdriver
import requests
import json
import time

# set the default profile
DEFAULT_PROFILE = {
    "name": "Windows stealthfox profile with random settings (LA)",
    "navigator": {
        "language": "English"
    }
}

# set the default os and browser
DEFAULT_OS = 'win'
DEFAULT_BROWSER = 'mimic'

# check the os and browser options
OS_OPTIONS = ['win', 'mac', 'lin']
BROWSER_OPTIONS = ['mimic', 'stealthfox']

# set the default urls and ports
BASE_URL = 'http://127.0.0.1'
V1_URL_EXT = 'api/v1/profile'
V2_URL_EXT = 'api/v2'
DEFAULT_PORT = 35000


# make a manager
class MLAManager(Manager):
    def __init__(self, filename=None, current_proxy=None, port=DEFAULT_PORT):
        # call the parent initialization
        super(MLAManager, self).__init__(filename, current_proxy)

        # set the v1 and v2 urls
        self.v1_url = f"{BASE_URL}:{port}/{V1_URL_EXT}"
        self.v2_url = f"{BASE_URL}:{port}/{V2_URL_EXT}"

    # make a function to make the profile (takes language parameter to allow integrability across platforms)
    def make_profile(self, profile=DEFAULT_PROFILE, operating_system=DEFAULT_OS, browser=DEFAULT_BROWSER, device=None, language=None, name=None):
        # set the name if there is not yet one
        if not name:
            profile['name'] = self.random_name()
        else:
            profile['name'] = name

        # set the profile os and browser
        profile['os'] = operating_system
        profile['browser'] = browser

        # catch any errors from wrong os or browser
        if profile['os'] not in OS_OPTIONS:
            print(
                f"Operating system choice of {profile['os']} not in {OS_OPTIONS}")
            return None
        if profile['browser'] not in BROWSER_OPTIONS:
            print(
                f"Browser choice of {profile['browser']} not in {BROWSER_OPTIONS}")
            return None

        # get the proxy
        proxy = self.get_proxy()

        # set the profile proxy
        profile['network'] = {'proxy': proxy}
        print(profile)

        # request body is the profile
        try:
            info = requests.post(f"{self.v2_url}/profile", json=profile).json()
            print(f"Make profile response: {info}")
        except JSONDecodeError:
            print(f"Unable to make {profile}")
            return None

        try:
            profile_id = info['uuid']
            print(f"Created browser profile {profile_id} on proxy {proxy}")
        except KeyError:
            print(info)
            profile_id = None

        return profile_id

    # make a function to delete a profile
    def delete_profile(self, profile_id):
        raw = requests.delete(f"{self.v2_url}/profile/{profile_id}")

        if raw.status_code == 204:
            # check if there is an error in the json
            try:
                info = raw.json()
            except JSONDecodeError:
                # multilogin gives no api response if it works
                return True

            print(info)
            if info['status'] == 'ERROR':
                print(
                    f"API error from multilogin: {info['message']} ({profile_id})")
                return False
        else:
            return False

    def get_profiles(self):
        try:
            info = requests.get(f"{V2_URL}/profile").json()
        except JSONDecodeError:
            print('Unable to get profiles')
            return None

        return info

    # make a function to stop a profile
    # will return true or false based on close status
    def stop_profile(self, profile_id):
        raw = requests.get(f"{self.v1_url}/stop",
                           params={'profileId': profile_id})

        if raw.status_code == 200:
            print(f"Stop profile response: {raw.json()}")
            if raw.json()['status'] == 'ERROR':
                print(raw.json())
                return False
            else:
                return True
        else:
            return False

    # make a function to check if a profile is active (based on the id)
    def is_profile_active(self, profile_id):
        raw = requests.get(f"{self.v1_url}/active")

        if raw.status_code == 200:
            return True
        else:
            return False


# make a function that creates a Multilogin browser
def create_mla_browser(profile_id, open_retries, retry_interval, port=None):
    # if no port is specified add one (this is better as it allows this function to be used in a constructor)
    if not port:
        port = DEFAULT_PORT

    # set a default driver variable
    driver = None

    # loop on retries
    for i in range(open_retries):
        # try checking the profile availability
        try:
            check_url = f"http://127.0.0.1:{port}/api/v1/profile/active"
            check_params = {'profileId': profile_id}
            check_resp = requests.get(check_url, check_params)

            if check_resp.status_code == 200:
                # break the loop when verified
                # this will return true if the browser is already open
                create = not check_resp.json()['value']
                break
            else:
                create = False
        except requests.exceptions.ConnectionError:
            print(
                f"Failed to open multilogin on port {port} ({profile_id})")
            create = False

        # wait for the next one
        time.sleep(retry_interval)

    if create:
        # try opening the bot on a loop
        for i in range(open_retries):
            mla_url = f"http://127.0.0.1:{port}/api/v1/profile/start?automation=true&profileId=" + profile_id
            resp = requests.get(mla_url)
            try:
                mla_json = resp.json()
                driver = webdriver.Remote(
                    command_executor=mla_json['value'], desired_capabilities={})

                print('Driver created for ' + profile_id)
                create = True

                # break the loop on creation
                break
            except KeyError:
                # log the attempt
                print(f"Attempt {i+1} to open {profile_id} failed")
                create = False
            except json.decoder.JSONDecodeError:
                print(
                    f"Multilogin failed to give a response ({profile_id})")
                create = False

        if not create:
            print('No driver created for ' + profile_id)

    return driver
