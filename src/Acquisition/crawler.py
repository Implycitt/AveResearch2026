'''
    Crawler for scraping users from iNaturalist.
    @file crawler.py
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