from databases.user_database import UserDatabase
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from routes.utils import login_required, get_database
from messages import get_ratio_message, get_random_greeting, get_random_recommendation

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    db = get_database()
    books = db.get_all_books()
    total_books = len(books)
    read_books = [book for book in books if book["read"]]
    favourite_books = [book for book in books if book["favourite"]]
    currently_reading_book = db.get_currently_reading()
    goal = db.get_reading_goal()

    ratio = 0
    if total_books > 0:
        ratio = round(len(read_books) / total_books * 100, 1)

    dashboard_data = {
        "read_books": len(read_books),
        "favourite_books": favourite_books[:5],
        "currently_reading": currently_reading_book,
        "reading_goal": {
            "goal": goal,
            "completed": len(read_books)
        }
    }

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        dashboard=dashboard_data,
        ratio=ratio,
        greeting=get_random_greeting(),
        message=get_ratio_message(ratio / 100),
        recommendation=get_random_recommendation()
    )

@dashboard_bp.route("/new_message")
@login_required
def new_message():
    db = get_database()
    ratio = db.get_read_ratio()
    return jsonify({
        "greeting": get_random_greeting(),
        "message": get_ratio_message(ratio),
        "recommendation": get_random_recommendation() 
    })

@dashboard_bp.route("/set_goal", methods=["POST"])
@login_required
def set_goal():
    db = get_database()
    new_goal = request.form["goal"]
    print(new_goal)
    db.set_reading_goal(new_goal)
    books = db.get_all_books()
    total_books = len(books)
    read_books = [book for book in books if book["read"]]
    favourite_books = [book for book in books if book["favourite"]]
    currently_reading_book = db.get_currently_reading()
    goal = db.get_reading_goal()
    print(goal)


    ratio = 0
    if total_books > 0:
        ratio = round(len(read_books) / total_books * 100, 1)

    dashboard_data = {
        "read_books": len(read_books),
        "favourite_books": favourite_books[:5],
        "currently_reading": currently_reading_book,
        "reading_goal": {
            "goal": goal,
            "completed": len(read_books)
        }
    }

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        dashboard=dashboard_data,
        ratio=ratio,
        greeting=get_random_greeting(),
        message=get_ratio_message(ratio / 100),
        recommendation=get_random_recommendation()
    )
