import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta
from openpyxl import Workbook
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(filename='weather_data_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BasePage:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def find(self, locator):
        try:
            return self.driver.find_element(*locator)
        except NoSuchElementException:
            logging.warning(f"Element not found: {locator}")
            return None

    def click(self, locator, retries=3):
        while retries > 0:
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(locator)).click()
                return
            except TimeoutException:
                retries -= 1
                logging.warning(f"Retrying click for: {locator}. Attempts left: {retries}")
        logging.error(f"Failed to click element after retries: {locator}")

class CalendarSelector(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.current_time = datetime.now()

    def set_previous_day(self):
        self.current_time -= timedelta(days=1)

    def get_formatted_date(self):
        day = self.current_time.strftime("%A").capitalize()
        month = self.current_time.strftime("%B").capitalize()
        day_num = self.current_time.day
        year = self.current_time.year
        return day, month, day_num, year

    def get_current_date_string(self):
        return self.current_time.strftime("%d/%m/%Y")

    def is_end_of_month(self):
        next_day = self.current_time + timedelta(days=1)
        return next_day.month != self.current_time.month

class DetailsAndSave(BasePage):
    def __init__(self, driver, workbook, filename, calendar_selector):
        super().__init__(driver)
        self.count = 0
        self.workbook = workbook
        self.sheet = workbook.active
        self.headers_written = False
        self.filename = filename
        self.calendar_selector = calendar_selector
        self.processed_dates = set()  

    def click_close_table(self):
        close_button = (By.XPATH, "(//button[@class='btn-close' and @data-bs-dismiss='modal'])[2]")
        self.click(close_button)

    def read_the_table(self):
        wait = WebDriverWait(self.driver, 10)
        detail_table_button = (By.XPATH, "//button[@class='btn btn-light me-1']")
        show_more_button = (By.XPATH, "//button[@class='btn btn-primary ms-auto']")
        overlay_locator = (By.CLASS_NAME, "loading-overlay")

       
        wait.until(EC.invisibility_of_element_located(overlay_locator))

        
        detail_button = self.find(detail_table_button)
        if detail_button:
            self.driver.execute_script("arguments[0].click();", detail_button)

            
            if self.count < 2:
                try:
                    wait.until(EC.visibility_of_element_located(show_more_button)).click()
                    self.count += 1
                except TimeoutException:
                    logging.warning("Show more button not found or not clickable.")

           
            try:
                table = self.find((By.XPATH, "//table[contains(@class, 'table-striped')]"))
                rows = table.find_elements(By.TAG_NAME, "tr")

                for i, row in enumerate(rows):
                    if i == 0 and not self.headers_written:
                        headers = [header.text for header in row.find_elements(By.TAG_NAME, "th")]
                        self.sheet.append(["Date"] + headers)
                        self.headers_written = True
                    else:
                        cells = row.find_elements(By.XPATH, "./th | ./td")
                        row_data = [datetime.now().strftime("%Y-%m-%d")] + [cell.text for cell in cells]
                        self.sheet.append(row_data)

                self.save_to_excel()
                
                
                current_date = self.calendar_selector.get_current_date_string()
                self.processed_dates.add(current_date)  # İşlenen tarihi kaydet
                print(f"{current_date} tablosu işlendi.")
                logging.info(f"{current_date} tablosu işlendi ve kaydedildi.")
            except NoSuchElementException:
                logging.error("Table not found.")
            self.click_close_table()
        else:
            logging.error("Detail table button not found.")

    def save_to_excel(self):
        self.workbook.save(self.filename)
        logging.info(f"Weather data has been saved to '{self.filename}'.")

class TryPage(BasePage):
    def __init__(self, driver, start_date_url):
        super().__init__(driver)
        self.driver.get(start_date_url)
        self.workbook = Workbook()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.filename = f"weather_data_{timestamp}.xlsx"
        self.calendar_selector = CalendarSelector(driver)
        self.details_and_save = DetailsAndSave(driver, self.workbook, self.filename, self.calendar_selector)

    def run(self):
        reject_button = (By.XPATH, "//button[@class='btn btn-light ms-auto']")
        date_button = (By.XPATH, "//button[@class='btn btn-light px-4 px-md-3']")
        calendar_point = (By.CSS_SELECTOR, "svg.vc-svg-icon:nth-of-type(1)")
        
        self.driver.maximize_window()
        self.click(reject_button)

        for _ in range(3650):
            attempts = 0
            max_attempts = 5  
            
            while attempts < max_attempts:
                try:
                    
                    WebDriverWait(self.driver, 20).until(EC.invisibility_of_element_located((By.CLASS_NAME, "offcanvas-backdrop")))

                    
                    self.click(date_button)

                    
                    if self.calendar_selector.is_end_of_month():
                        self.click(calendar_point)

                    day, month, day_num, year = self.calendar_selector.get_formatted_date()
                    dynamic_xpath = (By.XPATH, f"//span[@aria-label='{day}, {month} {day_num}, {year}']")
                    logging.info(f"Dynamic XPath: {dynamic_xpath}")

                    
                    element = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(dynamic_xpath))
                    actions = ActionChains(self.driver)
                    actions.double_click(element).perform()

                    
                    current_date_str = self.calendar_selector.get_current_date_string()
                    if current_date_str in self.details_and_save.processed_dates:
                        logging.warning(f"Date {current_date_str} already processed. Skipping to the next date.")
                        self.calendar_selector.set_previous_day()
                        break 

                    
                    self.details_and_save.read_the_table()
                    self.calendar_selector.set_previous_day()
                    
                    
                    break
                    
                except TimeoutException:
                    attempts += 1
                    logging.error(f"Timeout on date: {day}, {month} {day_num}, {year}. Attempt {attempts}/{max_attempts}.")
                    
                    if attempts == max_attempts:
                        logging.error(f"Skipping date: {day}, {month} {day_num}, {year} after {max_attempts} attempts.")
                        self.calendar_selector.set_previous_day()  
                    else:
                        
                        WebDriverWait(self.driver, 2).until(EC.invisibility_of_element_located((By.CLASS_NAME, "offcanvas-backdrop")))

                except Exception as e:
                    logging.error(f"Unexpected error occurred on date: {day}, {month} {day_num}, {year}. Error: {e}")
                    break

        self.driver.quit()

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")  

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        start_date_url = "https://meteostat.net/en/place/tr/istanbul?s=17060&t=2024-11-06/2024-11-06"
        try_page = TryPage(driver, start_date_url)
        try_page.run()
    except Exception as e:
        logging.error(f"Bir hata oluştu: {e}")
    finally:
        driver.quit()
