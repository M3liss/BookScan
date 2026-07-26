import requests
from services.isbn_check import scan_isbn_from_webcam


OPENLIBRARY_URL = "https://openlibrary.org"


def search_isbn(isbn):
    """
    Search a book by ISBN using OpenLibrary.
    Returns a book dictionary or None.
    """

    isbn = clean_isbn(isbn)

    if not isbn:
        return None

    url = (
        f"{OPENLIBRARY_URL}/api/books"
        f"?bibkeys=ISBN{isbn}"
        f"&format=json"
        f"&jscmd=data"
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        print(f"ISBN lookup failed: {e}")
        return None

    book = data.get(f"ISBN{isbn}")

    if not book:
        return None

    authors = book.get("authors", [])

    author = (
        authors[0].get("name")
        if authors
        else "Unknown"
    )

    return {
        "isbn": isbn,
        "title": book.get("title", "Unknown"),
        "author": author,
        "genre": None,
        "cover": get_cover_url(isbn)
    }


def search_title(title):

    url = (
        f"{OPENLIBRARY_URL}/search.json"
        f"?title={title}"
        f"&limit=10"
        f"&fields=*,edition_key,isbn"
    )

    return search_openlibrary(url)


def search_author(author):
    """
    Search a book by author.
    """

    url = (
        f"{OPENLIBRARY_URL}/search.json"
        f"?author={author}"
        f"&limit=10"
        f"&fields=*,edition_key,isbn"
    )

    return search_openlibrary(url)


def search_openlibrary(url):
    """
    Generic OpenLibrary search handler.
    """

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        print(f"OpenLibrary search failed: {e}")
        return None

    return pick_best_book(data)

def get_isbn_from_edition(edition_key):

    url = (
        f"{OPENLIBRARY_URL}/books/"
        f"{edition_key}.json"
    )

    try:

        response = requests.get(
            url,
            timeout=5
        )

        response.raise_for_status()

        data=response.json()

    except Exception:
        return None


    # Editions sometimes contain:
    # isbn_10 / isbn_13

    if "isbn_13" in data:

        return clean_isbn(
            data["isbn_13"][0]
        )


    if "isbn_10" in data:

        return clean_isbn(
            data["isbn_10"][0]
        )


    return None

def extract_isbn(book):

    isbns = book.get("isbn", [])

    for isbn in isbns:

        isbn = clean_isbn(isbn)

        if isbn and len(isbn) == 13:
            return isbn


    for isbn in isbns:

        isbn = clean_isbn(isbn)

        if isbn:
            return isbn


    editions = book.get(
        "edition_key",
        []
    )


    for edition in editions[:5]:

        isbn = get_isbn_from_edition(
            edition
        )

        if isbn:
            return isbn


    return None

def pick_best_book(result_json):

    docs = result_json.get("docs", [])

    if not docs:
        return None

    best = docs[0]

    isbn = extract_isbn(best)

    return {
        "isbn": isbn,
        "title": best.get("title", "Unknown"),
        "author": best.get(
            "author_name",
            ["Unknown"]
        )[0],
        "genre": (
            best.get("subject", [None])[0]
        ),
        "cover": get_cover_url(isbn)
    }



def clean_isbn(isbn):
    """
    Removes spaces and dashes from ISBN.
    """

    if not isbn:
        return None

    return (
        str(isbn)
        .replace("-", "")
        .replace(" ", "")
        .strip()
    )


def get_cover_url(isbn):
    """
    Returns OpenLibrary cover URL.
    """

    if not isbn:
        return None

    return (
        f"https://covers.openlibrary.org/isbn/{isbn}-L.jpg"
    )


def check_webcam():
    """
    Complete webcam -> ISBN -> OpenLibrary pipeline.
    """

    isbn = scan_isbn_from_webcam()

    if not isbn:
        return None, None, None

    book = search_isbn(isbn)

    if not book:
        return (
            isbn,
            "Unknown",
            "Unknown"
        )

    return (
        isbn,
        book["title"],
        book["author"]
    )


if __name__ == "__main__":

    print(search_title("The Hobbit"))
    print(search_author("J.R.R. Tolkien"))
    print(search_isbn("9780261103573"))