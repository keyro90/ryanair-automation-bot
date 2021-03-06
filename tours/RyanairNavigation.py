import logging
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from common.configuration import gc

logger = logging.getLogger("main")


class RyanairNavigation:

    def __init__(self, start_wanted_str, end_wanted_str, departure, destination):
        self.__start_wanted_str = start_wanted_str
        self.__end_wanted_str = end_wanted_str
        self.__departure = departure
        self.__destination = destination

    def __send_keys_delay(self, elem, text, secs: float = 0):
        for c in text:
            elem.send_keys(c)
            sleep(secs)

    def run(self):
        dt_start_wanted = datetime(*[int(s) for s in self.__start_wanted_str.split('-')])
        dt_end_wanted = datetime(*[int(s) for s in self.__end_wanted_str.split('-')])
        options = Options()
        options.headless = gc["headless"]
        driver = webdriver.Firefox(options=options, executable_path=gc["driver_pathname"])
        driver.get("https://www.ryanair.com/it/it")
        dt_now = datetime.today()
        if dt_now >= dt_start_wanted:
            logger.error(f"Start date {dt_start_wanted} is less than today")
            return
        distance_month = (dt_start_wanted.year - dt_now.year) * 12 + (dt_start_wanted.month - dt_now.month)
        try:
            logger.info("Accepting Cookie")
            elem_departure = driver.find_element(By.ID, "input-button__departure")
            elem_destination = driver.find_element(By.ID, "input-button__destination")
            elem_class_cookie = driver.find_element(By.CLASS_NAME, "cookie-popup-with-overlay__button")
            logger.info("Typing Departure")
            sleep(2)
            ActionChains(driver).click(elem_class_cookie).perform()
            sleep(2)
            ActionChains(driver).click(elem_departure).perform()
            sleep(1)
            ActionChains(driver).key_down(Keys.CONTROL).send_keys("A").key_up(Keys.CONTROL).send_keys(
                Keys.DELETE).perform()
            self.__send_keys_delay(elem_departure, self.__departure, 0.1)
            sleep(2)
            ActionChains(driver).click(elem_destination).perform()
            sleep(2)
            logger.info("Typing Destination")
            # Tenerife (Sud)
            self.__send_keys_delay(elem_destination, self.__destination, 0.1)
            ActionChains(driver).key_down(Keys.ENTER).perform()
            # sleep(2)
            sleep(2)
            # data-id="TFS"
            elem_tenerife = driver.find_element(By.XPATH, "//span[contains(@data-id,'TFS')]")
            ActionChains(driver).click(elem_tenerife).perform()
            sleep(3)
            logger.info("Start date Departure")
            elem_start_date = driver.find_element(By.XPATH, "//div[contains(@data-ref, 'input-button__dates-from')]")
            ActionChains(driver).click(elem_start_date).perform()
            sleep(2)
            elem_parent_months = driver.find_element(By.XPATH, "//div[contains(@class, 'm-toggle__scrollable-items')]")
            elem_months = elem_parent_months.find_elements(By.XPATH,
                                                           "//div[contains(@class, 'm-toggle__scrollable-item ng-star-inserted')]")
            ActionChains(driver).click(elem_months[distance_month]).perform()
            sleep(3)
            elem_data_choose = driver.find_element(By.XPATH,
                                                   f"//div[contains(@data-id, '{(dt_start_wanted.strftime('%Y-%m-%d'))}')]")
            if 'calendar-body__cell--disabled' in elem_data_choose.get_attribute('class').split():
                logger.info("start date is disabled")
                raise Exception("start date is disabled")
            ActionChains(driver).click(elem_data_choose).perform()
            sleep(1)
            logger.info("End date Departure")
            elem_data_choose_end = driver.find_element(By.XPATH,
                                                       f"//div[contains(@data-id, '{(dt_end_wanted.strftime('%Y-%m-%d'))}')]")
            if 'calendar-body__cell--disabled' in elem_data_choose_end.get_attribute('class').split():
                logger.info("end date is disabled")
                raise Exception("end date is disabled")
            ActionChains(driver).click(elem_data_choose_end).perform()
            sleep(2)
            logger.info("Click on search")
            elem_fatto = driver.find_element(By.XPATH,
                                             "//button[contains(@class, 'passengers__confirm-button')]")
            ActionChains(driver).click(elem_fatto).perform()
            sleep(2)
            logger.info("Checkbox agreements")
            check_box = driver.find_element(By.XPATH,
                                            "//ry-checkbox[contains(@data-ref,'terms-of-use__terms-checkbox')]")
            ActionChains(driver).click(check_box).perform()
            sleep(2)
            elem_search = driver.find_element(By.XPATH, "//button[contains(@data-ref, 'flight-search-widget__cta')]")
            ActionChains(driver).click(elem_search).perform()
            logger.info("Waiting page prices")
            sleep(20)
            # page with prices
            elem_uls = driver.find_elements(By.XPATH, "//ul[contains(@class, 'ng-trigger-listSlide')]")
            # elem_date_carousel = el.find_elements(By.TAG_NAME, "li")
            # elem_central_date = elem_date_carousel[2]
            logger.info("Scraping prices")
            elem_integers = elem_uls[0].find_elements(By.TAG_NAME, "li")[2].find_elements(By.XPATH,
                                                                                          "//span[contains(@class, 'price__integers carousel-date-price--selected')]")
            elem_decimalss = elem_uls[0].find_elements(By.TAG_NAME, "li")[2].find_elements(By.XPATH,
                                                                                           "//span[contains(@class, 'price__decimals carousel-date-price--selected ng-star-inserted')]")
            elem_fares_left = driver.find_elements(By.XPATH, "//span[contains(@class, 'price-fares-left')]")
            fares_dep = None
            fares_dest = None
            if elem_fares_left:
                if len(elem_fares_left) > 0:
                    fares_dep = elem_fares_left[0].text
                if len(elem_fares_left) > 1:
                    fares_dest = elem_fares_left[1].text
            price_start = float(f"{elem_integers[0].text}.{elem_decimalss[0].text}")
            price_end = float(f"{elem_integers[1].text}.{elem_decimalss[1].text}")
            return price_start, price_end, fares_dep, fares_dest
        except Exception as e:
            logger.error(e)
            return None, None, None, None
        finally:
            driver.quit()
