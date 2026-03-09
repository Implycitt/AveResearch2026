from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

from driver import Driver
import messenger
from Data.users import Users

def startPageCrawl(primaryDriver: webdriver) -> set:
    userLinks = primaryDriver.find_elements(By.CLASS_NAME, "userlink")
    userLinks += primaryDriver.find_elements(By.CLASS_NAME, "large")
    userLinks = extractName(userLinks)
    return createUserLinks(userLinks)

def findAll(url: str, webDriver: Driver) -> set:
    webDriver.connectUrl(url)
    primaryDriver = webDriver.driver

    followers = primaryDriver.find_elements(By.CLASS_NAME, "readable")
    followers = extractName(followers)

    remove = ["View Observations", "View Lists", "View Journal"]
    for i in remove:
        if i not in followers:
            continue
        followers.remove(i)
    return createUserLinks(followers)

def extractName(userLinks: set) -> set:
    outLinks = set()
    for element in userLinks:
        outLinks.add(element.text)
    return outLinks

def createUserLinks(usersList: set) -> None:
    outURLs = set()
    base = "https://inaturalist.org/people/"
    for user in usersList:
        outURLs.add(base + str(user))

    return outURLs

def crawl() -> None:
    webDriver = Driver()
    userData = Users()
    primaryDriver = webDriver.driver

    load_dotenv(dotenv_path="./in/.env")
    messenger.login(webDriver)
    webDriver.connectUrl("https://inaturalist.org/people")

    unvisitedUrls = startPageCrawl(primaryDriver)
    visited = set()

    while (len(unvisitedUrls) != 0):
        nextLink = unvisitedUrls.pop()
        if nextLink in visited:
            continue

        success = webDriver.connectUrl(nextLink)
        if (success):
            visited.add(nextLink)
            followingUrl, followersUrl = nextLink + "/following", nextLink + "/followers"
            connections = findAll(followingUrl, webDriver) | findAll(followersUrl, webDriver)

            for connection in connections:
                unvisitedUrls.add(connection)

            messenger.Messenger(nextLink[31:], webDriver)

        print("visited: ", len(visited) , " remaining: ", len(unvisitedUrls))

    userData.writeUsers(visited)

