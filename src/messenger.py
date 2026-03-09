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

