from core.BaseBot.platforms.Multilogin import create_mla_browser
from core.BaseBot.platforms.gologin import create_gologin_browser
from core.BaseBot.platforms.Kameleo import create_kameleo_browser
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException, NoSuchWindowException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import random
import time
import eel

# change to make headless or not
HEADLESS = False

DEFAULT_WAIT_INCREMENT = 5
DEFAULT_SCROLL_INCREMENT = 1
DEFAULT_SCROLL_RETRIES = 100
DEFAULT_OPEN_RETRIES = 10
DEFAULT_PLATFORM = 'multilogin'

# set to really high number to load everything
BOTTOM_PIXELS = 100000000

# set some cookie words to look for
DEFAULT_COOKIE_WORDS = ['accept', 'ok']


# make the standard bot class
class Bot:
    def __init__(self, platform=DEFAULT_PLATFORM, port=None, profile_id=None, token=None, chromedriver_path=None, wait_increment=DEFAULT_WAIT_INCREMENT, proxy=None, headless=HEADLESS, retries=DEFAULT_SCROLL_RETRIES, scroll_increment=DEFAULT_SCROLL_INCREMENT, open_retries=DEFAULT_OPEN_RETRIES, retry_interval=DEFAULT_WAIT_INCREMENT, browser=None):

        self.wait_increment = wait_increment
        self.scroll_increment = scroll_increment
        self.retries = retries

        # save it for logs
        self.profile_id = profile_id

        # save the browser type for close
        self.platform = platform

        # get a browser profile
        if not bool(profile_id):
            # import the test module
            from webdriver_manager.chrome import ChromeDriverManager

            # open a blank driver
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        elif 'gologin' == platform:
            # open the gologin browser and save the reference to the object (to kill it later)
            self.gl, self.driver = create_gologin_browser(
                profile_id, token, open_retries, retry_interval, chromedriver_path)
        elif 'multilogin' == platform:
            # open multilogin
            driver = create_mla_browser(
                profile_id, open_retries, retry_interval, port=port)
            self.driver = driver
        elif 'kameleo' == platform:
            # open kameleo
            driver = create_kameleo_browser(
                profile_id, open_retries, retry_interval, browser, port=port)
            self.driver = driver
        else:
            # set driver to none and mention that the platform is not recognized
            self.driver = None
            print(f"{platform} is not a recognized platform")

        # set the create variable for later checking
        self.create = bool(self.driver)

        # verify the bot
        try:
            import verify
        except ImportError:
            import sys
            print('Failed licensing check.')
            sys.exit()

        if self.create:
            # maximize the window
            self.driver.maximize_window()

            # log the first tab
            self.first_tab_handle = self.driver.current_window_handle

    # go to a proxy site and check it out
    def checkProxy(self):
        self.driver.get(
            'https://www.google.com/search?q=wha+is+my+ip&oq=wha+is+my+ip&aqs=chrome..69i57j0l7.2101j0j7&sourceid=chrome&ie=UTF-8')
        return(self.driver.find_element(By.XPATH,
                                        '//span[@style = "font-size:20px"]').text)

    # get many cookies
    def get_cookie(self, site, browser_interactions, cookie_words=DEFAULT_COOKIE_WORDS):
        # switch to home tab
        self.switch_to_home_tab()

        self.driver.get(site)
        eel.sleep(self.wait_increment)

        # set accepted to false
        accepted_cookie = False

        # get all the buttons
        buttons = self.driver.find_elements(By.XPATH, '//button')

        # iterate over the buttons and accept the right cookies
        for button in buttons:
            button_text = button.text.strip().lower()

            matches = [word for word in cookie_words if word in button_text]

            if len(matches) > 0:
                try:
                    button.click()
                    print(
                        f"Clicked '{button_text.title()}' to accept cookies on {site} ({self.profile_id})")
                    accepted_cookie = True
                    eel.sleep(self.wait_increment)
                    break
                except ElementClickInterceptedException:
                    print(f"Click to accept cookie denied on {site}")
                    pass

        if not accepted_cookie:
            print(f"Did not find cookies to accept on {site}")

        # if cookies have been accepted, attempt to click the a tags
        a_tags = self.driver.find_elements(By.XPATH, '//a')

        # have a counter of pages visited and tag attempts
        pages_visited = 0
        tag_attempts = 0
        while (pages_visited < browser_interactions) and (tag_attempts < len(a_tags)):
            # try to visit one, but except it if it is not interactable
            try:
                random.choice(a_tags).click()
                eel.sleep(self.wait_increment)

                # if this works, get new a tags
                a_tags = self.driver.find_elements_by_xpath('//a')

                # reset the tag attempts counter
                tag_attempts = 0
            except (ElementNotInteractableException, ElementClickInterceptedException):
                tag_attempts += 1
                continue

            # if it makes it here, increment the pages visited
            pages_visited += 1

    # get many cookies
    def get_cookies(self, sites, min_browser_interactions, max_browser_interactions, cookie_words=DEFAULT_COOKIE_WORDS):
        # make the cookie words all lower case and stripped
        cookie_words = [word.strip().lower() for word in cookie_words]

        # goes into the sites
        for site in sites:
            self.get_cookie(site, random.randint(
                min_browser_interactions, max_browser_interactions), cookie_words=cookie_words)

    # make a function to scroll if necessary
    def scroll(self, scrolls=1, return_to_top=False):
        for scroll in range(scrolls):
            self.driver.execute_script(
                f"window.scrollTo(0, {BOTTOM_PIXELS});")
            print(f"Scrolling to bottom ({self.profile_id})")
            eel.sleep(self.scroll_increment)

        if return_to_top:
            self.driver.execute_script("window.scrollTo(0, 0);")

    # scroll down and click an element
    def scroll_click(self, element, return_to_top=False):
        if return_to_top:
            self.driver.execute_script("window.scrollTo(0, 0);")

        clicked = False

        for _ in range(self.retries):
            try:
                element.click()
                eel.sleep(self.wait_increment)
                clicked = True
                break
            except ElementNotInteractableException:
                pass
            except ElementClickInterceptedException:
                pass

            # try different scroll techniques
            try:
                element.send_keys(Keys.PAGE_DOWN)
            except ElementNotInteractableException:
                self.driver.execute_script('window.scrollBy(0,250)')

            eel.sleep(self.scroll_increment)

        return clicked

    # make a function to scroll to a particular element
    def scroll_to(self, element):
        self.driver.execute_script(
            'arguments[0].scrollIntoView(true)', element)

    # make a function to hover click
    def hover_click(self, element):
        hover = ActionChains(self.driver).move_to_element(
            element).click()
        hover.perform()

    # make a way to reset the frame
    def set_frame(self, xpath):
        # get into the right frame
        iframe = self.driver.find_element(By.XPATH, xpath)
        self.driver.switch_to.frame(iframe)

    # function for uploading a file: this is not working
    def upload_file(self, file_fp):
        send_input = ActionChains(self.driver)
        send_input.send_keys(file_fp + Keys.ENTER)
        send_input.perform()

    # make a way to open a new tab
    def open_tab(self):
        # open a new tab
        self.driver.execute_script("window.open('');")

        self.driver.switch_to.window(self.driver.window_handles[1])

    # make a way to close the tab
    def close_tab(self):
        # close the tab
        self.driver.close()

        # switch to the og tab
        self.driver.switch_to.window(self.driver.window_handles[0])

    # make a function to switch back to the home tab
    def switch_to_home_tab(self):
        try:
            self.driver.switch_to.window(self.first_tab_handle)
        except NoSuchWindowException:
            pass

    # close the bot
    def close(self, close_method='quit'):
        if close_method == 'keys':
            print(f"Browser quit with keys started ({self.profile_id})")

            some_tag = self.driver.find_element(By.XPATH, '//html')
            some_tag.send_keys(Keys.ALT + Keys.F4)
        elif close_method == 'windows':
            # get the tabs
            print(f"Browser quit with windows started ({self.profile_id})")
            handles = self.driver.window_handles

            # close each tab
            for handle in handles:
                self.driver.switch_to.window(handle)
                self.driver.close()
        else:
            print(f"Browser quit with .quit() started ({self.profile_id})")
            self.driver.quit()

        if self.platform:
            if 'gologin' in self.platform.lower():
                self.gl.stop()

        # set that the bot is no longer created
        self.create = False
