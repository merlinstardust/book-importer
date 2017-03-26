from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import smtplib
from getpass import getpass
import csv

import time, re, sys, datetime

recordID = "y"
recordISBN = "y"
csvName = ""
headers = ["author", "title"]
driver = ""

def createHeaders():
    global headers
    if recordID == "y":
        headers.append("goodReadsID")
    if recordISBN == "y":
        headers.append("ISBN")

def bookNotFound(book):
    with open(csvName + "-NotFound.csv", "a") as f:
        writer = csv.DictWriter(f, headers)
        writer.writerow(book)

def recordNewInfo(book, grID, ISBN):
    hasString = ""
    if recordID == "y": 
        book["goodReadsID"] = grID
        hasString += "-hasID"
    if recordISBN == "y": 
        book["ISBN"] = ISBN
        hasString += "-hasISBN"
    with open(csvName + hasString + ".csv", "a") as f:
        writer = csv.DictWriter(f, headers)
        writer.writerow(book)

def getID():
    return driver.find_element_by_xpath("//best_book[1]/id").text

def getISBN():
    elt = driver.find_element_by_xpath("//meta[@property='good_reads:isbn']")
    return elt.get_attribute("content")

def getBooks():
    books = []

    try: open(csvName + ".csv")
    except: print "  opening %s failed", csvFile

    with open(csvName + ".csv", "r") as f:
        reader = csv.DictReader(f, headers)
        for row in reader:
            if (headers[0] and headers[1]) in row:
                books.append(row)
            else: print "  found row, didn't match"
    return books

def loginToFacebook(fbEmail, fbPass):
    facebookURL = "http://www.facebook.com"
    driver.get(facebookURL)
    driver.find_element_by_name("email").send_keys(fbEmail)
    driver.find_element_by_name("pass").send_keys(fbPass)

def addBooks(books, shelf):
    goodReadsURL = "http://www.goodreads.com/"
    searchBaseURL = goodReadsURL + "search.xml"
    addBaseURL = goodReadsURL + "shelf/add_to_shelf.xml"
    bookBaseURL = goodReadsURL + "book/show/"
    key = "y1EJ27Ran80OLamoB7Wjw"

    driver.get(goodReadsURL)

    count = 1
    numBooks = str(len(books))
    for b in books:
        atBook = str(count)
        print "adding " + atBook + "of" + numBooks + ": ", b
        author = b["author"]
        title = b["title"].replace("-", " ")
        query = author + " " + title

        searchURL = searchBaseURL + "?key=" + key + "&q=" + query
        driver.get(searchURL)
        #print "  " + searchURL

        numResults = int(driver.find_element_by_xpath("//total-results").text)
        if numResults > 0:
            bookID = getID()
            #print "  found, bookid is " + bookID
            addURL = addBaseURL + "?name=" + shelf + "&book_id=" + bookID
            driver.get(addURL)
            print "  added"
            isbn = ""
            if recordISBN == "y":
                bookURL = bookBaseURL + bookID
                driver.get(bookURL)
                isbn = getISBN()
                #print "  isbn " + isbn
            if recordID == "y" or recordISBN == "y":
                recordNewInfo(b, bookID, isbn)
        else:
            print "  no results found for ", b
            bookNotFound(b)
        count += 1

def main():
    print "Book Importer"
    print "This program imports books from a CSV file with rows of AUTHOR,TITLE"
    print "At the moment, this program logs in to GoodReads through Facebook."
    print "This program will not store your username or password anywhere."

    global recordID, recordISBN, csvName, driver
    recordID = str(raw_input("Record GoodReads IDs? (Y/n): ")).lower()
    if recordID in '\n': recordID = "y"
    recordISBN = str(raw_input("Record the ISBN? (Y/n): ")).lower()
    if recordISBN in '\n': recordISBN = "y"
    createHeaders()

    csvFile = str(raw_input("CSV with books to add (default books.csv): "))
    if csvFile in '\n': csvFile = "books.csv"
    csvName = csvFile[0:-4]
    books = getBooks()

    fbEmail = str(raw_input("Facebook email: "))
    fbPass = str(raw_input("Facebook password: "))
    shelf = str(raw_input("Shelf to add to: "))
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    loginToFacebook(fbEmail, fbPass)
    addBooks(books, shelf)

if __name__ == "__main__":
    main()
