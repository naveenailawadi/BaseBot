from core.constants import BOTTOM_PIXELS, DEFAULT_WAIT_INCREMENT
from core.BaseBot.platforms.Multilogin import create_mla_browser
from core.BaseBot.platforms.gologin import create_gologin_browser
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import random
import time

# change to make headless or not
HEADLESS = False

DEFAULT_SCROLL_RETRIES = 100
DEFAULT_OPEN_RETRIES = 10
DEFAULT_PLATFORM = 'multilogin'


# make the standard bot class
class Bot:
    def __init__(self, platform=DEFAULT_PLATFORM, profile_id=None, token=None, chromedriver_path=None, wait_increment=DEFAULT_WAIT_INCREMENT, proxy=None, headless=HEADLESS, retries=DEFAULT_SCROLL_RETRIES, open_retries=DEFAULT_OPEN_RETRIES, retry_interval=DEFAULT_WAIT_INCREMENT):
        self.wait_increment = wait_increment
        self.retries = retries

        # save it for logs
        self.profile_id = profile_id

        # save the browser type for close
        self.platform = platform

        # get a browser profile
        if not profile_id:
            # import the test module
            from webdriver_manager.chrome import ChromeDriverManager

            # open a blank driver
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        elif 'gologin' in platform.lower():
            # open the gologin browser and save the reference to the object (to kill it later)
            self.gl, self.driver = create_gologin_browser(
                profile_id, token, open_retries, retry_interval, driver_path)
        else:
            # open multilogin
            driver = create_mla_browser(
                profile_id, open_retries, retry_interval)
            self.driver = driver

        # set the create variable for later checking
        if self.driver:
            self.create = True
        else:
            self.create = False

        # verify the bot
        try:
            import verify
            import sys
        except ImportError:
            # delete itself
            import os
            os.remove('core/bots.py')
            print('Failed licensing check.')
            sys.exit()

        if self.create:
            # maximize the window
            self.driver.maximize_window()

            # log the first tab
            self.first_tab_handle = self.driver.current_window_handle

    # go to a proxy site and check it out
    def checkProxy(self, user, passw):
        self.driver.get(
            'https://www.google.com/search?q=wha+is+my+ip&oq=wha+is+my+ip&aqs=chrome..69i57j0l7.2101j0j7&sourceid=chrome&ie=UTF-8')
        return(self.driver.find_element(By.XPATH,
                                        '//span[@style = "font-size:20px"]').text)

    # get many cookies
    def get_cookie(self, site, browser_interactions):
        # switch to home tab
        self.switch_to_home_tab()

        self.driver.get(site)

        # get all the buttons
        buttons = self.driver.find_elements_by_xpath('//button')

        # iterate over the buttons and accept the right cookies
        for button in buttons:
            button_text = button.text.strip().lower()

            if ('accept' in button_text):
                button.click()
                print(
                    f"Clicked '{button_text.title()}' to accept cookies on {site} ({self.profile_id})")
                time.sleep(self.wait_increment)
                break

        # if cookies have been accepted, attempt to click the a tags
        a_tags = self.driver.find_elements_by_xpath('//a')

        # have a counter of pages visited and tag attempts
        pages_visited = 0
        tag_attempts = 0
        while (pages_visited < browser_interactions) and (tag_attempts < len(a_tags)):
            # try to visit one, but except it if it is not interactable
            try:
                random.choice(a_tags).click()
                time.sleep(self.wait_increment)

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
    def get_cookies(self, sites, min_browser_interactions, max_browser_interactions):
        # goes into the sites
        for site in sites:
            self.get_cookie(site, random.randint(
                min_browser_interactions, max_browser_interactions))

    # make a function to scroll if necessary
    def scroll(self, scrolls=1, return_to_top=False):
        for scroll in range(scrolls):
            self.driver.execute_script(
                f"window.scrollTo(0, {BOTTOM_PIXELS});")
            print(f"Scrolling to bottom ({self.profile_id})")
            time.sleep(self.wait_increment)

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
                time.sleep(self.wait_increment)
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

            time.sleep(self.wait_increment / 3)

        return clicked

    # make a function to hover click
    def hover_click(self, element):
        hover = ActionChains(self.driver).move_to_element(
            element).click()
        hover.perform()

    # make a function to switch back to the home tab
    def switch_to_home_tab(self):
        self.driver.switch_to.window(self.first_tab_handle)

    # close the bot
    def close(self):
        print(f"Browser quit started ({self.profile_id})")
        self.driver.quit()

        if 'gologin' in self.platform.lower():
            self.gl.stop()
