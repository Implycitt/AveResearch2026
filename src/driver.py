from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os, sys
from dotenv import load_dotenv

class Driver:
    def __init__(self) -> None:
        chromeOptions = Options()
        chromeOptions.add_argument("--headless=new")
        chromeOptions.add_argument("--disable-gpu")
        chromeOptions.add_argument("--disable-renderer-backgrounding")
        chromeOptions.add_argument("--disable-background-timer-throttling")
        chromeOptions.add_argument("--disable-backgrounding-occluded-windows")
        chromeOptions.add_argument('--disable-dev-shm-usage')
        chromeOptions.add_argument("--no-sandbox")

        if (sys.platform.startswith("linux")):
            self.driver = self.linuxWebdriver(chromeOptions)

        self.driver = webdriver.Chrome(options=chromeOptions)

    def linuxWebdriver(self, chromeOptions) -> webdriver:
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chromeOptions)

    def connectUrl(self, url: str) -> bool:
        try:
            self.driver.get(url)
            return True
        except:
            return False

    def terminate(self) -> None:
        self.driver.quit()

    def typeIntoElement(self, element, text: str) -> None:
        return element.send_keys(text)

    def pressButton(self, buttonElement) -> None:
        buttonElement.click()
