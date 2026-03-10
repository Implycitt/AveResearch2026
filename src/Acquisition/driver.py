'''
    Driver class for handling Selenium WebDriver interactions, including connecting to URLs, typing into elements, and pressing buttons.
    @file driver.py
    @author Quentin Bordelon
    <pre>
    Date: 10-03-2026

    MIT License

    Contact Information: qborde1@lsu.edu
    Copyright (c) 2026 Quentin Bordelon

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    </pre>
''' 

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
