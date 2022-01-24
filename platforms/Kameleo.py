
from core.BaseBot.platforms.Managers import Manager
from kameleo.local_api_client.kameleo_local_api_client import KameleoLocalApiClient
from kameleo.local_api_client.builder_for_create_profile import BuilderForCreateProfile
from kameleo.local_api_client.models.server_py3 import Server
from kameleo.local_api_client.models.problem_response_py3 import ProblemResponseException
from selenium import webdriver
import traceback
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

DEFAULT_LANGUAGE = 'en-gb'  # https://www.andiamo.co.uk/resources/iso-language-codes/

BASE_URL = 'http://localhost:5050'


# make a manager
class KameleoManager(Manager):
    def __init__(self, filename=None, current_proxy=None):
        # call the parent init
        super(KameleoManager, self).__init__(filename, current_proxy)

        # make a client to use
        self.client = KameleoLocalApiClient(BASE_URL)

    # make a function to make the profile
    def make_profile(self, profile=DEFAULT_PROFILE, operating_system=DEFAULT_OS, browser=DEFAULT_BROWSER, device=DEFAULT_DEVICE, language=DEFAULT_LANGUAGE):
        # get all the base profiles that can be used
        base_profiles = self.client.search_base_profiles(
            device_type=device, os_family=operating_system, browser_product=browser, language=language)

        # get a random proxy
        proxy = self.get_proxy()

        # make the profile request (need proxies)
        create_profile_request = BuilderForCreateProfile.for_base_profile(
            base_profiles[0].id).set_recommended_defaults().set_proxy('http', Server(host=proxy['host'], port=int(proxy['port']), id=proxy['username'], secret=proxy['password'])).set_launcher('chromium').build()

        # make the profile
        try:
            profile = self.client.create_profile(body=create_profile_request)
            print(f"Created browser profile {profile.id} on proxy {proxy}")
        except Exception as e:
            print(e)
            return None

        return profile.id

    # make a function to delete a profile
    def delete_profile(self, profile_id):
        try:
            self.client.delete_profile(profile_id)
            return True
        except Exception as e:
            print(f"Delete {e} ({profile_id})")

            return False

    # profiles are not available for kameleo
    def get_profiles(self):
        '''
        try:
            info = requests.get(f"{V2_URL}/profile").json()
        except JSONDecodeError:
            print('Unable to get profiles')
            return None
        '''
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
def create_kameleo_browser(profile_id, open_retries, retry_interval, browser=DEFAULT_BROWSER):
    # set a browser default
    driver = None

    print(f"Launching browser type: {browser}")

    # make the options depending on the browser
    '''
    if browser == 'chrome':
        options = webdriver.ChromeOptions()

        # add the options
        options.add_experimental_option("kameleo:profileId", profile_id)
    elif browser == 'firefox':
        options = webdriver.FirefoxOptions()

        # add the options
        options.set_preference("kameleo:profileId", profile_id)
        options.set_preference("kameleo:profileId", profile_id)
    elif browser == 'edge':
        options = webdriver.EdgeOptions()

        # add the options
        options.add_experimental_option("kameleo:profileId", profile_id)
    elif browser == 'safari':
        options = webdriver.Safari.Options()

        # add the options
        options.add_experimental_option("kameleo:profileId", profile_id)
    else:
        # output that there are no options for the given browser and return none (for the browser)
        print(f"Could not match kameleo with browser type: {browser}")
        return None

    # disable notifications
    options.add_argument('--disable-notifications')
    '''
    options = webdriver.ChromeOptions(
    )  # using the chromium emulator for everything (per support recommendation)

    # add the options
    options.add_experimental_option("kameleo:profileId", profile_id)

    # make a kemeleo manager (does not need proxies)
    manager = KameleoManager()

    # try opening the bot on a loop
    for i in range(open_retries):

        try:
            manager.client.start_profile(profile_id)
            driver = webdriver.Remote(
                command_executor=f"{BASE_URL}/webdriver", options=options)

            print('Driver created for ' + profile_id)
            create = True

            # break the loop on creation
            break
        except ProblemResponseException as e:
            print(f"Kameleo Start {e} ({browser}: {profile_id})")
        except Exception:
            # output the error (for now)
            traceback.print_exc()

            create = False

        # wait before retrying
        time.sleep(retry_interval)

        # log the attempt
        print(f"Attempt {i+1} to open {profile_id} failed")

    if not create:
        print('No driver created for ' + profile_id)
    # else wait for kameleo to spin up the browser
    else:
        time.sleep(retry_interval)

    return driver
