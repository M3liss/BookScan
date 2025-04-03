import requests
from isbn_check import scan_isbn_from_webcam

def search_isbn(isbn):
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN{isbn}&format=json&jscmd=data"
    response = requests.get(url)
    data = response.json()
    obj = data.get(f"ISBN{isbn}")
    title = obj.get("title", "Unknown")
    author = obj.get("authors")[0].get("name") if obj.get("authors") else "Unknown"
    return title, author

def search_author(author):
    url = f"https://openlibrary.org/search.json?author={author}&sort=new"
    response = requests.get(url)
    print(response.json())

def search_title(title):
    a = 1

def check_webcam():
    result = scan_isbn_from_webcam()
    return result
#search_isbn("9781526610140")
#search_author("Tolkien")