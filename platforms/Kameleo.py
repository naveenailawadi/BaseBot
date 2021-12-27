from core.platforms.Managers import Manager
from core.platforms.kameleoSDK.kameleo.local_api_client.kameleo_local_api_client import KameleoLocalApiClient
from core.platforms.kameleoSDK.kameleo.local_api_client.builder_for_create_profile import BuilderForCreateProfile
from json.decoder import JSONDecodeError
from selenium import webdriver
import requests
import time

# set the default profile
DEFAULT_PROFILE = {
    "name": "Windows stealthfox profile with random settings (LA)",
    "navigator": {
        "language": "English"
    }
}

DEFAULT_DEVICE = "desktop"  # 'desktop', 'mobile'
DEFAULT_OS = "windows"  # 'windows', 'macos', 'linux', 'android', 'ios'
DEFAULT_BROWSER = "chrome"  # 'chrome', 'firefox', 'edge', 'safari'

BASE_URL = 'http://localhost:5050'


# make a manager
class KameleoManager(Manager):
    def __init__(self, filename=None):
        self.import_proxies(filename)

        # make a client to use
        self.client = KameleoLocalApiClient(BASE_URL)

    # make a function to make the profile
    def make_profile(self, profile=DEFAULT_PROFILE, operating_system=DEFAULT_OS, browser=DEFAULT_BROWSER, device=DEFAULT_DEVICE):
        # get all the base profiles that can be used
        base_profiles = self.client.search_base_profiles(
            device_type=device, os_family=operating_system, browser_product=browser)

        print(
            f"Base profiles provided ({len(base_profiles)}): {base_profiles}")

        # make the profile request as res
        create_profile_request = BuilderForCreateProfile.for_base_profile(
            base_profiles[0].id).set_recommended_defaults().build()

        # make the profile
        profile = self.client.create_profile(body=create_profile_request)

        # start the profile
        self.client.start_profile(profile.id)

        return profile.id

    # make a function to delete a profile
    def delete_profile(self, profile_id):
        self.client.delete_profile(profile_id)

        return True

    def get_profiles(self):
        '''
        try:
            info = requests.get(f"{V2_URL}/profile").json()
        except JSONDecodeError:
            print('Unable to get profiles')
            return None
        '''
        print('Get Profiles disabled for Kameleo')
        return {}

    # make a function to stop a profile
    # will return true or false based on close status
    def stop_profile(self, profile_id):
        self.client.stop_profile(profile_id)

    # make a function to check if a profile is active (based on the id)
    def is_profile_active(self, profile_id):
        '''
        raw = requests.get(f"{V1_URL}/active")

        if raw.status_code == 200:
            return True
        else:
            return False
         '''

        print('Profile activity disabled for Kameleo')

        return False


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
