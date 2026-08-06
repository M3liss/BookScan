import io
import os
import tempfile
import qrcode
from flask import (Blueprint, jsonify, render_template, request, redirect, url_for, session, send_file)
from werkzeug.utils import secure_filename

from routes.utils import (login_required, get_database,generate_mobile_login_token, start_session, verify_mobile_login_token)
from services.lookup import search_isbn, check_webcam, search_author, search_title
from services.isbn_check import scan_isbn_from_image

library_bp = Blueprint("library", __name__)

def _process_scan_upload(file_storage):
    """Save an uploaded image, scan it for an ISBN, look up the book, and
    add it to the library.

    Returns (book_dict, error_message) - exactly one of the two is None.
    """
    if file_storage is None or file_storage.filename == "":
        return None, "No file uploaded"

    filename = secure_filename(file_storage.filename)
    ext = os.path.splitext(filename)[1] or ".jpg"
    fd, path = tempfile.mkstemp(prefix="scan_", suffix=ext)
    os.close(fd)
    file_storage.save(path)

    try:
        isbn = scan_isbn_from_image(path)
        if not isbn:
            return None, "No ISBN found"
        book = search_isbn(isbn)
        if not book:
            return None, "Book not found"
        db = get_database()
        db.add_book(book["isbn"], book["title"], book["author"], book.get("genre", "Unknown"), "", "", "")
        return book, None
    finally:
        if os.path.exists(path):
            os.remove(path)


@library_bp.route("/library")
@login_required
def library():
    db = get_database()
    books = db.get_all_books()
    return render_template("library.html", books=books, reading_goal=db.get_read_ratio())


@library_bp.route("/scan", methods=["POST"])
@login_required
def scan():
    book, error = _process_scan_upload(request.files.get("file"))
    if error:
        status = 400 if error == "No file uploaded" else 404
        return error, status
    return redirect(url_for("library.library"))


@library_bp.route("/add_webcam")
@login_required
def add_by_webcam():
    db = get_database()
    try:
        isbn, title, author = check_webcam()
    except Exception as e:
        return f"Could not scan book: {e}", 400
    if not isbn:
        return "No ISBN found", 404
    db.add_book(isbn, "", "", "", False, False, False)
    return redirect(url_for("library.library"))


@library_bp.route("/add_book", methods=["POST"])
@login_required
def add_book():
    db = get_database()
    data = request.json
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    favourite = data.get("favourite", False)
    read = data.get("read", False)
    currently_reading = data.get("current_read", False)
    book = None
    if title:
        book = search_title(title=title)
    elif author:
        book = search_author(author=author)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    result = db.add_book(book["isbn"], book["title"], book["author"], book.get("genre", "Unknown"), favourite, read, currently_reading)
    if not result["success"]:
        return jsonify({"error": result["error"]}), 400
    return jsonify({"success": True, "book": book})


@library_bp.route("/edit_book", methods=["POST"])
@login_required
def edit_book():
    db = get_database()
    data = request.json
    book_id = data.get("id")
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    if not book_id:
        return jsonify({"error": "No book id provided"}), 400
    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    result = db.edit_book(int(book_id), title, author)
    return jsonify(result)


@library_bp.route("/delete_book", methods=["POST"])
@login_required
def delete_book():
    db = get_database()
    data = request.json
    book_ids = data.get("books", [])
    if not book_ids:
        return jsonify({"error": "No books selected"}), 400
    for book_id in book_ids:
        db.del_book(int(book_id))
    return jsonify({"success": True, "deleted": "Books deleted"})


@library_bp.route("/mark_favourite", methods=["POST"])
@login_required
def mark_favourite():
    db = get_database()
    data = request.json
    book_ids = data.get("books", [])
    if not book_ids:
        return jsonify({"error": "No books provided"}), 400
    for book_id in book_ids:
        db.toggle_fav(int(book_id))
    return jsonify({"success": True})


@library_bp.route("/mark_read", methods=["POST"])
@login_required
def mark_read():
    db = get_database()
    data = request.json
    book_ids = data.get("books", [])
    if not book_ids:
        return jsonify({"error": "No books provided"}), 400
    for book_id in book_ids:
        db.toggle_read(int(book_id))
    return jsonify({"success": True})


@library_bp.route("/mark_currently_reading", methods=["POST"])
@login_required
def mark_currently_reading():
    db = get_database()
    data = request.json
    book_id = data.get("book_id")
    if not book_id:
        return jsonify({"error": "No book provided"}), 400
    book_id = int(book_id)
    current = db.get_currently_reading()
    if current and current["id"] == book_id:
        db.clear_currently_reading()
        return jsonify({"success": True, "currently_reading": None})
    db.set_currently_reading(book_id)
    return jsonify({"success": True, "currently_reading": book_id})


@library_bp.route("/search_books")
@login_required
def search_books():
    db = get_database()
    query = request.args.get("q", "")
    books = db.search_books(query)
    return jsonify({"books": books})


@library_bp.route("/book/<int:book_id>")
@login_required
def book_details(book_id):
    db = get_database()
    book = db.get_book(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)


@library_bp.route("/reading_goal", methods=["GET", "POST"])
@login_required
def reading_goal():
    db = get_database()
    if request.method == "GET":
        return jsonify({"goal": db.get_reading_goal()})
    data = request.json
    goal = int(data.get("goal", 20))
    db.set_reading_goal(goal)
    return jsonify({"success": True, "goal": goal})

@library_bp.route("/mobile_qr")
@login_required
def mobile_qr():
    token = generate_mobile_login_token(session["user_id"])
    path = url_for("library.mobile_scan", token=token)
    LAN_IP = request.host.split(":")[0]
    PORT = request.host.split(":")[1] if ":" in request.host else 5000
    url = f"http://{LAN_IP}:{PORT}{path}"

    qr = qrcode.make(url)
    img = io.BytesIO()
    qr.save(img, "PNG")
    img.seek(0)
    return send_file(img, mimetype="image/png")

@library_bp.route("/mobile_scan", methods=["GET", "POST"])
@login_required
def mobile_scan():
    if request.method == "GET":
        token = request.args.get("token")
        if token:
            user_id = verify_mobile_login_token(token)
            if not user_id:
                return "<h2>This QR code has expired. Refresh the library page and scan a new one.</h2>", 400
            session.clear()
            start_session(user_id, session.get("username", ""))
            return redirect(url_for("library.mobile_scan"))
        return render_template("mobile_scan.html")

    book, error = _process_scan_upload(request.files.get("file"))
    if error:
        status = 400 if error == "No file uploaded" else 404
        return jsonify({"success": False, "error": error}), status
    return jsonify({"success": True, "book": book})


@library_bp.route("/mobile_scan_photo")
@login_required
def mobile_scan_photo():
    return render_template("mobile_scan_photo.html")


@library_bp.route("/mobile_camera_scan", methods=["POST"])
@login_required
def mobile_camera_scan():
    file = request.files.get("image")
    if file is None:
        return jsonify({"found": False, "error": "No image provided"}), 400

    book, error = _process_scan_upload(file)
    if error:
        return jsonify({"found": False, "error": error})
    return jsonify({"found": True, "book": book})


@library_bp.route("/upload_goodreads", methods=["POST"])
@login_required
def import_goodreads():
    file = request.files.get("goodreads_file") or request.files.get("file")
    if file is None:
        return jsonify({"error": "No file uploaded"}), 400

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    db = get_database()
    result = db.import_goodreads(file)
    if result.get("errors"):
        return jsonify({"success": False, "error": result["errors"][0], "imported": result["imported"], "skipped": result["skipped"]}), 400
    return jsonify({"success": True, "imported": result["imported"], "skipped": result["skipped"]})