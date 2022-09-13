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
DEFAULT_OS = "windows"
DEFAULT_BROWSER = "chrome"

# have the os and browser options
OS_OPTIONS = ['windows', 'macos', 'linux', 'android', 'ios']
BROWSER_OPTIONS = ['chrome', 'firefox', 'edge', 'safari']

DEFAULT_LANGUAGE = 'en-gb'  # https://www.andiamo.co.uk/resources/iso-language-codes/

# base url and port
BASE_URL = 'http://localhost'
DEFAULT_PORT = 5050


# make a manager
class KameleoManager(Manager):
    def __init__(self, filename=None, current_proxy=None, port=DEFAULT_PORT):
        # call the parent init
        super(KameleoManager, self).__init__(filename, current_proxy)

        # create a base url from the url and port
        self.base_url = f"{BASE_URL}:{port}"

        # make a client to use
        self.client = KameleoLocalApiClient(self.base_url)

    # make a function to make the profile
    def make_profile(self, profile=DEFAULT_PROFILE, operating_system=DEFAULT_OS, browser=DEFAULT_BROWSER, device=DEFAULT_DEVICE, language=DEFAULT_LANGUAGE):
        if operating_system not in OS_OPTIONS:
            print(
                f"Operating system choice of {operating_system} not in {OS_OPTIONS}")
            return None
        if browser not in BROWSER_OPTIONS:
            print(
                f"Browser choice of {browser} not in {BROWSER_OPTIONS}")
            return None

        # get all the base profiles that can be used
        base_profiles = self.client.search_base_profiles(
            device_type=device, os_family=operating_system, browser_product=browser, language=language)

        # return that there are no base profiles if that is the case
        if len(base_profiles) == 0:
            return None

        # get a random proxy
        proxy = self.get_proxy()

        # make the profile request (need proxies)
        create_profile_request = BuilderForCreateProfile.for_base_profile(
            base_profiles[0].id).set_recommended_defaults().set_proxy('http', Server(host=proxy['host'], port=int(proxy['port']), id=proxy['username'], secret=proxy['password'])).build()

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

    # get the profile IDs (rest is not useful)
    def get_profiles(self):
        profiles = self.client.list_profiles()
        return [{'profile_id': profile.id, 'browser': profile.browser.product} for profile in profiles]

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
def create_kameleo_browser(profile_id, open_retries, retry_interval, browser=DEFAULT_BROWSER, port=None):
    # set the port to something if it has not been set (allows for integration with other constructors)
    if not port:
        port = DEFAULT_PORT

    # set a browser default
    driver = None

    print(f"Launching browser type: {browser}")

    # make the options depending on the browser
    if browser == 'chrome':
        options = webdriver.ChromeOptions()
        options.add_experimental_option("kameleo:profileId", profile_id)
    elif browser == 'edge':
        options = webdriver.EdgeOptions()
        options.add_experimental_option("kameleo:profileId", profile_id)
    elif browser == 'safari':
        options = webdriver.ChromeOptions()
        options.add_experimental_option("kameleo:profileId", profile_id)
    elif browser == 'firefox':
        options = webdriver.FirefoxOptions()
        options.set_capability('kameleo:profileId', profile_id)
    else:
        # need to specify browser to start
        print('Must specify browser to start kameleo profiles.')
        return

    '''
    options = webdriver.ChromeOptions(
    )  # using the chromium emulator for everything (per support recommendation)
    '''

    # add the options
    if options:
        options.add_argument('--disable-notifications')

    # make a kemeleo manager (does not need proxies)
    manager = KameleoManager(port=port)

    # try opening the bot on a loop
    for i in range(open_retries):

        try:
            manager.client.start_profile(profile_id)

            # use the options if you have them
            driver = webdriver.Remote(
                command_executor=f"{manager.base_url}/webdriver", options=options)

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
