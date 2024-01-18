import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, make_response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from decimal import Decimal
from datetime import datetime, timedelta

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Initialize an empty dictionary to store stock prices and their last update time
cached_prices = {}

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    rows = db.execute("SELECT * FROM wallet WHERE id = ?;", user_id)

    if len(rows) != 0:
        wallet = db.execute(
            "SELECT stock_name, SUM(shares) AS shares FROM wallet WHERE id = ? GROUP BY stock_name;",
            user_id,
        )

        balance = db.execute("SELECT cash FROM users WHERE id = ?;", user_id)
        cash = round(balance[0]["cash"], 2)

        grandtotal = 0

        for item in wallet:
            stock_name = item["stock_name"]

            # Check if the stock price is in the cache and if it's still valid
            if stock_name in cached_prices:
                stock_info = cached_prices[stock_name]
                last_update_time = stock_info.get("last_update_time", None)

                if last_update_time and datetime.now() - last_update_time < timedelta(minutes=0.2):
                    # Use the cached price
                    stock_price = stock_info.get("price", 0)
                else:
                    # Update the price by making a new API call
                    stock_info = lookup(stock_name)
                    stock_price = stock_info.get("price", 0)
                    # Update the cache
                    cached_prices[stock_name] = {"price": stock_price, "last_update_time": datetime.now()}
            else:
                # If the stock is not in the cache, make a new API call
                stock_info = lookup(stock_name)
                stock_price = stock_info.get("price", 0)
                # Update the cache
                cached_prices[stock_name] = {"price": stock_price, "last_update_time": datetime.now()}

            item["price"] = round(float(stock_price), 2)
            item["total"] = round(item["shares"] * float(stock_price), 2)
            grandtotal += item["total"]
            item["price"] = usd(item["price"])
            item["total"] = usd(item["total"])

        grandtotal = round(grandtotal + cash, 2)

        # Create a response with a refresh header
        response = make_response(render_template(
            "index.html", wallet=wallet, cash=usd(cash), grandtotal=usd(grandtotal)
        ))

        # Refresh the page every 5 minutes (adjust the interval as needed)
        response.headers['Refresh'] = '300;'

        return response
    else:
        cash = db.execute("SELECT cash FROM users WHERE id = ?;", user_id)
        cash = cash[0]["cash"]
        shares = 0
        grandtotal = cash + shares

        return render_template("index.html", cash=usd(cash), grandtotal=usd(grandtotal))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        stock_data = lookup(symbol)

        if not symbol or not stock_data:
            return apology("Must provide a valid symbol", 400)

        # Check if shares is a positive number
        if not is_valid_number(shares):
            return apology("Must provide a valid positive number for shares", 400)

        shares_decimal = Decimal(shares)
        shares = int(round(shares_decimal))

        buy = "bought"
        price = stock_data["price"]
        user_id = session["user_id"]
        cash = Decimal(db.execute("SELECT cash FROM users WHERE id = ?;", user_id)[0]["cash"])
        transaction_value = Decimal(price) * shares

        if transaction_value > cash:
            return apology("Cannot afford the number of shares at the current price", 400)

        balance = cash - transaction_value
        db.execute(
            "INSERT INTO transactions (stock_name, tran_type, price, units, userId) VALUES (?, ?, ?, ?, ?);",
            symbol,
            buy,
            price,
            shares,
            user_id,
        )
        db.execute("UPDATE users SET cash = ? WHERE id = ?;", float(balance), user_id)

        rows = db.execute("SELECT * FROM wallet WHERE id = ?;", user_id)
        if rows:
            for item in rows:
                if item["stock_name"] == symbol:
                    units = db.execute(
                        "SELECT shares FROM wallet WHERE id = ? AND stock_name = ?;",
                        user_id,
                        symbol,
                    )[0]["shares"]
                    total = units + shares
                    db.execute(
                        "UPDATE wallet SET shares = ? WHERE id = ? AND stock_name = ?;",
                        total,
                        user_id,
                        symbol,
                    )
                    break
            else:
                db.execute(
                    "INSERT INTO wallet (id, stock_name, shares) VALUES (?, ?, ?);",
                    user_id,
                    symbol,
                    shares,
                )
        else:
            db.execute(
                "INSERT INTO wallet (id, stock_name, shares) VALUES (?, ?, ?);",
                user_id,
                symbol,
                shares,
            )

        flash(f"Purchased {shares} shares of {symbol} for {usd(transaction_value)}!")
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    history = db.execute(
        "SELECT * FROM transactions WHERE userId = ? ORDER BY id DESC;", user_id
    )

    for price in history:
        price["price"] = usd(price["price"])

    # Check if the user has made any transactions
    if not history:
        return render_template("history.html", history=None)  # Pass None to indicate no transactions

    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return apology("Must provide both username and password", 403)

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) != 1 or not check_password_hash(user[0]["pass_hash"], password):
            return apology("Invalid username and/or password", 403)

        session["user_id"] = user[0]["id"]
        flash(f"Welcome {username}!")
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol or not lookup(symbol):
            return apology("The symbol doesn't exist", 400)

        stock_data = [lookup(symbol)]
        stock_data[0]["price"] = usd(stock_data[0]["price"])

        return render_template("quoted.html", stocks=stock_data)
    else:
        return render_template("quote.html")


def validate_password_complexity(password):
    """
    Validate password complexity.
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Minimum length of 8 characters
    """
    pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+{}|":;<>,.?/~`]).{8,}$')
    return bool(re.match(pattern, password))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return apology("Must provide username, password, and confirmation", 400)

        if password != confirmation:
            return apology("Passwords do not match", 400)

        if not validate_password_complexity(password):
            return apology("Password must meet complexity requirements", 400)

        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing_user:
            return apology("Username already exists", 400)

        db.execute(
            "INSERT INTO users (username, pass_hash) VALUES (?, ?);",
            username,
            generate_password_hash(password, method="pbkdf2", salt_length=16),
        )

        flash("Registered!")
        return redirect("/login")

    else:
        return render_template("register.html")


def is_valid_number(value):
    try:
        float_value = float(value)
        return float_value.is_integer() and float_value > 0
    except ValueError:
        return False


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # ensure symbol and shares are submitted
        symbol = request.form.get("symbol")
        shares_input = request.form.get("shares")

        if not symbol or lookup(symbol) is None:
            return apology("You need to select a stock symbol from your portfolio", 400)

        if not shares_input or not is_valid_number(shares_input):
            return apology("Must provide a valid positive number for shares", 400)

        # get user id, the stock symbol and the dict with user shares
        user_id = session["user_id"]
        stock_name = symbol
        obj_shares = db.execute(
            "SELECT shares FROM wallet WHERE id = ? AND stock_name = ?;",
            user_id,
            stock_name,
        )

        # set units as the number of user shares and convert the desired amount to sell into a float
        units = obj_shares[0]["shares"]
        shares = float(shares_input)

        # ensure the valid range of shares owned by the user
        if shares < 1 or shares > units:
            return apology(
                "Must provide a positive number in the range of shares that you own",
                400,
            )

        # set the status of the operation, get stock data, set price and balance of shares
        sell = "sold"
        stock_data = lookup(stock_name)
        price = stock_data["price"]
        balance = units - shares

        # insert operation into the database into transactions table
        db.execute(
            "INSERT INTO transactions (stock_name, tran_type, price, units, userId) VALUES (?, ?, ?, ?, ?);",
            stock_name,
            sell,
            price,
            shares,
            user_id,
        )

        # if the user doesn't have shares anymore, delete it from the wallet, otherwise, update it
        if balance == 0:
            db.execute(
                "DELETE FROM wallet WHERE stock_name = ? AND id = ?;",
                stock_name,
                user_id,
            )
        else:
            db.execute(
                "UPDATE wallet SET shares = ? WHERE id = ? AND stock_name = ?;",
                balance,
                user_id,
                stock_name,
            )

        # set transaction value, get user cash, update user cash adding transaction value
        transaction_value = price * shares
        obj_cash = db.execute("SELECT cash FROM users WHERE id = ?;", user_id)
        cash = obj_cash[0]["cash"]
        total_cash = cash + transaction_value
        db.execute("UPDATE users SET cash = ? WHERE id = ?;", total_cash, user_id)

        # display a flash message, redirect to index
        flash(f"Sold {shares:.2f} shares of {stock_name} for {usd(transaction_value)}!")
        return redirect("/")

    else:
        # User reached route via GET (as by requesting a form via GET)
        # get user id
        user_id = session["user_id"]
        rows = db.execute("SELECT * FROM wallet WHERE id = ?;", user_id)
        # check if the user already has a wallet, if so, add the stock prices and show wallet content in the sell html
        if rows:
            wallet = db.execute(
                "SELECT stock_name, shares FROM wallet WHERE id = ?;", user_id
            )

            for item in wallet:
                obj = lookup(item["stock_name"])
                item["price"] = round(obj["price"], 2)

            return render_template("sell.html", wallet=wallet)
        else:
            # the user doesn't have a wallet, return the sell html without data
            return render_template("sell.html")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user password"""
    if request.method == "POST":
        user_id = session["user_id"]
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Validate input
        if not current_password or not new_password or not confirmation:
            return apology("Must provide current password, new password, and confirmation", 400)

        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        if not user or not check_password_hash(user[0]["pass_hash"], current_password):
            return apology("Invalid current password", 400)

        if new_password != confirmation:
            return apology("New passwords do not match", 400)

        if not validate_password_complexity(new_password):
            return apology("New password must meet complexity requirements", 400)

        # Update password in the database
        db.execute(
            "UPDATE users SET pass_hash = ? WHERE id = ?",
            generate_password_hash(new_password, method="pbkdf2", salt_length=16),
            user_id,
        )

        flash("Password changed successfully!")
        return redirect("/")

    else:
        return render_template("change_password.html")


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "POST":
        amount = float(request.form.get("amount"))
        card_number = request.form.get("card_number")
        expiration_date = datetime.strptime(request.form.get("expiration_date"), "%Y-%m").date()

        # Perform credit card validation
        card_type, is_valid = validate_credit_card(card_number)

        if not is_valid:
            flash("Invalid credit card number")
            return redirect("/add_cash")

        # Assuming you have a 'users' table with a 'cash' column representing the user's balance
        user_id = session["user_id"]
        user_balance = db.execute("SELECT cash FROM users WHERE id = ?;", user_id)[0]["cash"]

        # Update the user's balance
        new_balance = user_balance + amount
        db.execute("UPDATE users SET cash = ? WHERE id = ?;", new_balance, user_id)

        flash(f"Successfully added ${amount} to your account! Your new balance is ${new_balance}. Card Type: {card_type}")

        return redirect("/")
    else:
        return render_template("add_cash.html")


def validate_credit_card(card_number):
    # Implement CS50 Credit card validation algorithm with card type detection
    total_sum = 0
    reverse_card_number = card_number[::-1]

    for i, digit_char in enumerate(reverse_card_number):
        digit = int(digit_char)

        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9

        total_sum += digit

    is_valid = total_sum % 10 == 0

    # Detect card type based on the first few digits
    if is_valid:
        if card_number.startswith("4"):
            card_type = "Visa"
        elif card_number.startswith(("51", "52", "53", "54", "55")):
            card_type = "MasterCard"
        elif card_number.startswith(("34", "37")):
            card_type = "American Express"
        else:
            card_type = "Unknown"
    else:
        card_type = "Invalid"

    return card_type, is_valid


if __name__ == "__main__":
    app.run(debug=True)
