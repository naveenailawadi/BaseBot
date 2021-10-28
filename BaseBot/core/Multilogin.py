from core.Managers import Manager
from json.decoder import JSONDecodeError
from selenium import webdriver
import requests
import time

# set the default profile
DEFAULT_PROFILE = {
    "name": "Windows stealthfox profile with random settings (LA)",
    "os": "win",
    "browser": "stealthfox",
    "navigator": {
        "language": "English"
    }
}

BASE_URL = 'http://127.0.0.1:35000/api/v2'


# make a manager
class MLAManager(Manager):
    def __init__(self, filename=None):
        self.import_proxies(filename)

    # make a function to make the profile
    def make_profile(self, profile=DEFAULT_PROFILE):
        # change the profile name
        profile['name'] = f"Random Profile {self.random_string()}"

        # change the profile proxy
        profile['network'] = {'proxy': self.random_proxy()}

        # request body is the profile
        try:
            info = requests.post(f"{BASE_URL}/profile", json=profile).json()
        except JSONDecodeError:
            print(f"Unable to make {profile}")
            return None

        try:
            profile_id = info['uuid']
            print(f"Created browser profile {profile_id}")
        except KeyError:
            print(info)
            profile_id = None

        return profile_id

    # make a function to delete a profile
    def delete_profile(self, profile_id):
        try:
            raw = requests.delete(f"{BASE_URL}/profile/{profile_id}")
        except JSONDecodeError:
            print(f"Unable to delete {profile_id}")
            return False

        if raw.status_code == 204:
            deleted = True
        else:
            deleted = False

        return deleted

    def get_profiles(self):
        try:
            info = requests.get(f"{BASE_URL}/profile").json()
        except JSONDecodeError:
            print('Unable to get profiles')
            return None

        return info


# make a function that creates a Multilogin browser
def create_mla_browser(profile_id, open_retries, retry_interval):
    # set a default driver variable
    driver = None

    # loop on retries
    for i in range(open_retries):
        # try checking the profile availability
        try:
            check_url = 'http://127.0.0.1:35000/api/v1/profile/active'
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
                f"Failed to open multilogin on port 35000 ({profile_id})")
            create = False

        # wait for the next one
        time.sleep(retry_interval)

    if create:
        # try opening the bot on a loop
        for i in range(open_retries):
            mla_url = 'http://127.0.0.1:35000/api/v1/profile/start?automation=true&profileId=' + profile_id
            resp = requests.get(mla_url)
            mla_json = resp.json()
            try:
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

        if not create:
            print('No driver created for ' + profile_id)

    return driver
