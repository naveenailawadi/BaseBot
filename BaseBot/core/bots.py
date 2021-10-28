from core.Multilogin import create_mla_browser
from core import constants
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time


class TwitterBot:
    def __init__(self, profile_id, wait_increment=constants.DEFAULT_WAIT_INCREMENT, open_retries=constants.DEFAULT_OPEN_RETRIES, retry_interval=constants.DEFAULT_WAIT_INCREMENT):
        self.wait_increment = wait_increment

        # save it for logs
        self.profile_id = profile_id

        self.driver = create_mla_browser(
            profile_id, open_retries, retry_interval)

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

            time.sleep(self.wait_increment)

        return clicked

    # make a function to hover click
    def hover_click(self, element):
        hover = ActionChains(self.driver).move_to_element(
            element).click()
        hover.perform()

    # make a function to scroll if necessary
    def scroll(self, scrolls=1, return_to_top=False):
        for scroll in range(scrolls):
            self.driver.execute_script(
                f"window.scrollTo(0, {constants.BOTTOM_PIXELS});")
            print(f"Scrolling to bottom ({self.profile_id})")
            time.sleep(self.wait_increment)

        if return_to_top:
            self.driver.execute_script("window.scrollTo(0, 0);")

    def close(self):
        self.driver.quit()
