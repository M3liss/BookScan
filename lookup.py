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
    return pick_best_book(response.json())

def search_title(title):
    url = f"https://openlibrary.org/search.json?title={title}&sort=new"
    response = requests.get(url)
    return pick_best_book(response.json())

def pick_best_book(result_json):
    return {
        "isbn": 1234766,
        "title": "TEEEST",
        "author": "TEEEEEEEEEEEST",
        "genre": None,
        "favourite": False,
        "read": False
    }

    docs = result_json.get("docs", [])

    if not docs:
        return None

    # First result = best result (sorted by OpenLibrary)
    best = docs[0]

    isbn = best.get("isbn", [None])[0]
    title = best.get("title", "Unknown Title")
    author = best.get("author_name", ["Unknown Author"])[0]

    return {
        "isbn": isbn,
        "title": title,
        "author": author,
        "genre": None,
        "favourite": False,
        "read": False
    }

def check_webcam():
    isbn = scan_isbn_from_webcam()
    print(isbn)
    title, author = search_isbn(isbn)
    return isbn, title, author


if __name__ == "__main__":
    #search_isbn("9781526610140")
    search_author("Tolkien")
    #search_title("The Hobbit")
    #check_webcam()
