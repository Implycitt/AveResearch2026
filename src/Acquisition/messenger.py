'''
    Module for sending messages to iNaturalist users.
    @file messenger.py
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
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv

from driver import Driver

def getHeaderBody() -> tuple:
    with open("./in/message.txt", 'r') as file:
        header, body = map(str, file.read().split('\n\n'))
    return (header, body.strip('\n'))

def login(webDriver: Driver) -> None:
    email, password = map(str, (os.getenv('EMAIL'), os.getenv('PASSWORD')))
    primaryDriver = webDriver.driver
    webDriver.connectUrl("https://Inaturalist.org/login")

    emailField = primaryDriver.find_element(By.ID, "user_email")
    passwordField = primaryDriver.find_element(By.ID, "user_password")

    webDriver.typeIntoElement(emailField, email)
    webDriver.typeIntoElement(passwordField, password)

    webDriver.pressButton(primaryDriver.find_element(By.NAME, "commit"))

def sendMessage(webDriver: Driver, header: str, body: str) -> None:
    primaryDriver = webDriver.driver

    headerField = primaryDriver.find_element(By.ID, "message_subject")
    bodyField = primaryDriver.find_element(By.ID, "message_body")

    webDriver.typeIntoElement(headerField, header)
    webDriver.typeIntoElement(bodyField, body)

    webDriver.pressButton(primaryDriver.find_element(By.NAME, "commit"))

def Messenger(user: str, webDriver: webdriver) -> None:
    baseUrl = "https://www.inaturalist.org/messages/new?to="

    header, body = map(str, getHeaderBody())

    newUrl = baseUrl + user
    print(newUrl)
    webDriver.connectUrl(newUrl)
    sendMessage(webDriver, header, body)

