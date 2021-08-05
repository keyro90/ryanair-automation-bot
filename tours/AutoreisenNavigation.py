import logging
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

logger = logging.getLogger("main")


class AutoreisenNavigation:

    def __init__(self, pickup_location, return_location, start_date, end_date, exe_path, headless=True):
        self.__pickup_location = pickup_location
        self.__return_location = return_location
        self.__start_date = start_date
        self.__end_date = end_date
        self.__exe_path = exe_path
        self.__headless = headless

    def found_by_inner_text(self, elem_select, find_inner):
        options_pickup = elem_select.find_elements(By.TAG_NAME, "option")
        for opt in options_pickup:
            if find_inner in opt.text:
                return opt
        return None

    def select_day_calendar(self, driver, elem_calendar, start_date, from_date=None):
        dt_from = datetime.today()
        if from_date:
            dt_from = datetime.strptime(from_date, "%Y-%m-%d %H:%M")
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        distance_month = (start_date_obj.year - dt_from.year) * 12 + (start_date_obj.month - dt_from.month)
        for time in range(0, distance_month):
            a_next = elem_calendar.find_element(By.XPATH, "//a[@title='Next']")
            ActionChains(driver).click(a_next).perform()
            sleep(1)
        elem_day = elem_calendar.find_element(By.XPATH,
                                              f"//a[text()='{start_date_obj.day}']")
        ActionChains(driver).click(elem_day).perform()

    def run(self):
        options = Options()
        options.headless = self.__headless
        driver = webdriver.Firefox(options=options, executable_path=self.__exe_path)
        driver.get("https://autoreisen.com/car-hire/car-hire.php")
        try:
            sleep(3)
            elem_select_pickup = driver.find_element(By.ID, "recogida")
            elem_select_return = driver.find_element(By.ID, "devolucion")
            opt_pickup = self.found_by_inner_text(elem_select_pickup, self.__pickup_location)
            opt_return = self.found_by_inner_text(elem_select_return, self.__return_location)
            opt_pickup.click()
            sleep(1)
            opt_return.click()
            sleep(4)
            elem_pick_row = driver.find_element(By.XPATH, "//div[contains(@class, 'date-row first-row')]")
            elem_button_calendar = elem_pick_row.find_element(By.TAG_NAME, "button")
            ActionChains(driver).click(elem_button_calendar).perform()
            sleep(3)
            elem_calendar = driver.find_element(By.ID, "ui-datepicker-div")
            self.select_day_calendar(driver, elem_calendar, self.__start_date)
            sleep(2)
            elem_calendar = driver.find_element(By.ID, "ui-datepicker-div")
            self.select_day_calendar(driver, elem_calendar, self.__end_date, self.__start_date)
            sleep(2)
            elem_hora_1 = driver.find_element(By.ID, "hora-1")
            elem_hora_2 = driver.find_element(By.ID, "hora-2")
            for opt in elem_hora_1.find_elements(By.TAG_NAME, "option"):
                if opt.text == self.__start_date.split(" ")[1]:
                    opt.click()
            for opt in elem_hora_2.find_elements(By.TAG_NAME, "option"):
                if opt.text == self.__end_date.split(" ")[1]:
                    opt.click()
            sleep(3)
            elem_submit = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Go']")
            ActionChains(driver).click(elem_submit).perform()
            sleep(8)
            elem_first_art = driver.find_element(By.TAG_NAME, "article")
            title_car = elem_first_art.find_element(By.XPATH, "//strong[@class='title']")
            a_price = elem_first_art.find_element(By.XPATH, "//a[contains(@class, 'price add')]/span")
            return title_car.text, a_price.text
        except Exception as e:
            logger.error(e)
            return None, None
        finally:
            driver.quit()
