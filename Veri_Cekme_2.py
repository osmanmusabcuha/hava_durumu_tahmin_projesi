from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta
import time
from openpyxl import Workbook

class BasePage:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def find(self, locator):
        return self.driver.find_element(*locator)

    def click(self, locator):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(locator)).click()

class CalendarSelector(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.current_time = datetime.now()

    def set_local_time(self):
        self.current_time -= timedelta(days=1)

    def get_formatted_date(self):
        day = self.current_time.strftime("%A").capitalize()
        month = self.current_time.strftime("%B").capitalize()
        day_num = self.current_time.day
        return day, month, day_num

    def is_end_of_month(self):
        """Kontrol etmek için son gün olup olmadığını belirler."""
        next_day = self.current_time + timedelta(days=1)
        return next_day.month != self.current_time.month

class DetailsAndSave(BasePage):
    def __init__(self, driver, workbook):
        super().__init__(driver)
        self.count = 0
        self.workbook = workbook
        self.sheet = workbook.active
        self.headers_written = False

    def click_close_table(self):
        close_button = (By.XPATH, "(//button[@class='btn-close' and @data-bs-dismiss='modal'])[2]")
        try:
            self.click(close_button)
        except NoSuchElementException:
            print("Close button not found, skipping.")

    def read_the_table(self):
        wait = WebDriverWait(self.driver, 8)
        detail_table_button = (By.XPATH, "//button[@class='btn btn-light me-1']")
        show_more_button = (By.XPATH, "//button[@class='btn btn-primary ms-auto']")

        try:
            self.click(detail_table_button)
            if self.count < 2:
                try:
                    wait.until(EC.visibility_of_element_located(show_more_button)).click()
                    self.count += 1
                except TimeoutException:
                    print("Show more button not found or not clickable.")
        except NoSuchElementException:
            print("Detail table button not found.")
            return

        try:
            table = self.find((
                By.XPATH,
                "//table[contains(@class, 'table') and contains(@class, 'table-striped') and contains(@class, 'table-bordered') "
                "and contains(@class, 'table-hover') and contains(@class, 'align-middle') and contains(@class, 'mb-0')]"
            ))
            rows = table.find_elements(By.TAG_NAME, "tr")

            for i, row in enumerate(rows):
                if i == 0 and not self.headers_written:
                    headers = row.find_elements(By.TAG_NAME, "th")
                    header_texts = [header.text for header in headers]
                    self.sheet.append(["Date"] + header_texts)
                    self.headers_written = True
                else:
                    cells = row.find_elements(By.XPATH, "./th | ./td")
                    row_data = [datetime.now().strftime("%Y-%m-%d")] + [cell.text for cell in cells]
                    self.sheet.append(row_data)

            print("Data row saved.")
            self.save_to_excel()
        except NoSuchElementException:
            print("Table not found.")
        self.click_close_table()

    def save_to_excel(self):
        self.workbook.save("weather_data_3.xlsx")
        print("Weather data has been saved to 'weather_data_3.xlsx'.")

class TryPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get("https://meteostat.net/en/place/tr/istanbul?s=17060&t=2024-11-06/2024-11-06")
        self.workbook = Workbook()
        self.calendar_selector = CalendarSelector(driver)
        self.details_and_save = DetailsAndSave(driver, self.workbook)

    def run(self):
        reject_button = (By.XPATH, "//button[@class='btn btn-light ms-auto']")
        date_button = (By.XPATH, "//button[@class='btn btn-light px-4 px-md-3']")
        calendar_point = (By.CSS_SELECTOR, "svg.vc-svg-icon:nth-of-type(1)")

        self.driver.maximize_window()
        time.sleep(3)

        try:
            self.click(reject_button)
        except NoSuchElementException:
            print("Reject button not found, continuing without clicking.")

        a = 3650
        while a != 1:
            try:
                self.click(date_button)

                if self.calendar_selector.is_end_of_month():
                    self.click(calendar_point)  

                
                day, month, day_num = self.calendar_selector.get_formatted_date()
                date = f"{day}, {month} {day_num}, 2024"
                dynamic_xpath = (By.XPATH, f"//span[@aria-label='{date}']")
                print(f"Dynamic XPath: {dynamic_xpath}")

                
                wait = WebDriverWait(self.driver, 10)
                element = wait.until(EC.element_to_be_clickable(dynamic_xpath))
                actions = ActionChains(self.driver)
                actions.double_click(element).perform()

                
                self.details_and_save.read_the_table()

                
                time.sleep(5)
                self.calendar_selector.set_local_time()
                a -= 1
            except Exception as e:
                print(f"Error: {e}")
                continue

        self.driver.quit()

if __name__ == "__main__":
    chrome_driver_path = "C:\\Users\\osman\\seleniumdrivers\\chrome-driver\\chromedriver-win64\\chromedriver.exe"
    chrome_options = Options()
    chrome_options.add_argument("--disable-popup-blocking")

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        try_page = TryPage(driver)
        try_page.run()
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        driver.quit()
