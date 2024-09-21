import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

from datetime import datetime
# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


# The date and time of the purchase
now = datetime.now()
date = now.strftime("%Y-%m-%d %H:%M:%S")

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

    # Querie which stocks the user owns, the numbers of shares owned in the database
    index_rows = db.execute("SELECT stock, SUM(shares) AS shares FROM purchase WHERE buyer_id = ? GROUP BY stock", session["user_id"])


    # Keep track of the grand total of the stocks
    stocks_total = 0

    # Keep track of the price if each stocks
    prices_list = []

    # Keep track of the total value of each stock
    total_values = []

    # For each stock
    for row in range(len(index_rows)):
        index_stock = index_rows[row]["stock"]
        index_shares = index_rows[row]["shares"]

        # The current price for each share
        look = lookup(index_stock)
        index_price = look["price"]

        # Add the price to the list of prices
        prices_list.append(usd(index_price))

        # The total value of the current stock
        total_value = index_price * index_shares

        # Add the total value to the list of total values
        total_values.append(usd(total_value))

        # Update the grand total of all the stocks
        stocks_total += total_value

    # The current balance of the user
    balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

    # Gand total (stock's total value + cash)
    grand_total = usd(stocks_total + balance[0]["cash"])

    # If user is new registrant
    if len(index_rows) == 0:
        return render_template("new.html")
    else:
        return render_template("index.html", rows=index_rows, stock=index_stock, shares=index_shares, price=index_price, total_values=total_values, prices_list=prices_list, cash=usd(balance[0]["cash"]), grand_total=(grand_total))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # If user reached route via POST
    if request.method == "POST":

        # Insure user has provided symbol
        if not request.form.get("symbol"):
            return apology("Must provide a symbol")

        # Sotre provided number of shares
        get_shares = request.form.get("shares").strip()

        try:
            # Check if shares contains only digits
            if not get_shares.isdigit():
                return apology("Must provide a positive number of shares")

            # Convert provided number of shares to an integer
            buy_shares = int(get_shares)

            # Insure number of shares is a positive integer
            if buy_shares <= 0 :
                return apology("Must provide a positive number of shares")

            # Store the stock quote
            purchase = lookup(request.form.get("symbol"))

            # If the look up is unsuccessful
            if purchase == None:
                return apology("Stock symbol does not exist")

            buy_price = purchase["price"]
            buy_symbol = purchase["symbol"]

            # Update user's cash:
            cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

            if cash[0]["cash"] < (buy_price * buy_shares):
                return apology("Insufficient balance")

            new_cash = cash[0]["cash"] - (buy_price * buy_shares)

            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"])

            # Insert purchase informations:
            # the buyer
            buyer_id = db.execute("SELECT id FROM users WHERE id = ?", session["user_id"])
            buyer_id = buyer_id[0]["id"]

            # The total cost of the purchase
            total = buy_shares * buy_price

            # Insert puchase INTO the purchase table
            db.execute("INSERT INTO purchase (buyer_id, stock, shares, price_per_share, total_price, purchase_date) VALUES(?, ?, ?, ?, ?, ?)", buyer_id, buy_symbol, buy_shares, buy_price, total, date)

            # Save the purchase in history:
            db.execute("INSERT INTO history (user_id, operation_type, stock, shares, price_per_share, total_price, purchase_date) VALUES(?, ?, ?, ?, ?, ?, ?)", session["user_id"], "purchase", buy_symbol, buy_shares, buy_price, total, date)

            # Redirect user to homepage
            return redirect("/")

        except ValueError:
            return apology("Invalid number of shares")
        except Exception:
            return apology("Coudn't process you request")

    # If user reached route via GET
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute("SELECT * FROM history")
    if len(rows) == 0:
            return render_template("new.html")
    else:
        return render_template("history.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # If user reached route via GET
    if request.method == "POST":

        # Insure user has provided symbol
        if not request.form.get("symbol"):
            return apology("Must provide a symbol")

        # Store the stock quote
        quote = lookup(request.form.get("symbol"))

        # If the look up is unsuccessful
        if quote == None:
            return apology("Stock symbol does not exist")

        quote_name = quote["name"]
        quote_price = quote["price"]
        quote_symbol = quote["symbol"]

        return render_template("quoted.html", quote=quote, name=quote_name, price=quote_price, symbol=quote_symbol)

    # If user reached route via POST
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # If the user reached route via POST
    if request.method == "POST":

        # Get form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if password meet all the requirements
        if not any(char.islower() for char in password):
            return apology("Password must contain at least one lowercase letter")

        if not any(char.isupper() for char in password):
            return apology("Password must contain at least one uppercase letter")

        if not any(not char.isalnum() for char in password):
            return apology("Password must contain at least one special character")

        if not any(not char.isdigit() for char in password):
            return apology("Password must contain at least one uppercase letter")

        if len(password) < 8:
            return apology("Password must contain at least 8 character")

        # Unsure that password was confirmed
        if password != confirmation:
            return apology("Password and confirmation don't match")

        # Check if the username already exists
        if len(db.execute("SELECT username FROM users WHERE username = ?", username)) != 0:
            return apology("Username already exists")

        # Insert the user into the users table
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))

        # Redirect user to home page
        return redirect("/login")

    # If the user reached route via GET
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # If user reached route via POST
    if request.method == "POST":

        # Store  and check the stock provided
        sell_stock = request.form.get("symbol")

        if not sell_stock:
            return apology("Must provid a stock")

        # Look up the stock
        stock = lookup(sell_stock)
        if stock == None:
            return apology("Invalid  stock")

        symbol = stock["symbol"]
        price = stock["price"]

        # Querie the stocks that user owns
        stocks = db.execute("SELECT DISTINCT stock FROM purchase WHERE buyer_id = ?", session["user_id"])

        try:

            if symbol not in [stock["stock"] for stock in stocks]:
                return apology("That stock is not in your assets")

            # Store and check the number of shares
            get_shares = request.form.get("shares").strip()

            # Insure that shares only contains digits
            if not get_shares or not get_shares.isdigit():
                return apology("Must provide a number of shares")
            else:
                # Convert shares to an integer
                shares = int(get_shares)

            # Insure number of shares is a positive integer
            if shares <= 0:
                return apology("Must provide a positive number of shares")

            # Insure user own that many shares
            owned_shares = db.execute("SELECT SUM(shares) AS n FROM purchase WHERE stock = ?", symbol)

            if shares > owned_shares[0]["n"]:
                return apology(f"You don't have that many shares of {symbol}")

            # Update nummber of shares
            db.execute("UPDATE purchase SET shares = shares - ? WHERE stock = ? AND buyer_id = ? LIMIT 1", shares, symbol, session["user_id"])
            
            purchase = db.execute("SELECT DISTINCT shares FROM purchase WHERE stock = ? AND buyer_id = ?", symbol, session["user_id"])

            # Delete the purchase if no shares are left
            left_shares = db.execute("SELECT SUM(shares) AS left FROM purchase WHERE stock = ? AND buyer_id = ?", symbol, session["user_id"])

            if left_shares[0]["left"] <= 0:
                db.execute("DELETE FROM purchase WHERE stock = ? AND buyer_id = ?", symbol, session["user_id"])

            if purchase[0]["shares"] <= 0:
                db.execute("DELETE FROM purchase WHERE stock = ? AND buyer_id = ?", symbol, session["user_id"])

            # Update user's cash:
            user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
            cash = user_cash[0]["cash"]

            cash += (price * shares)

            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])

            # Save the purchase in history:
            total = price * shares
            db.execute("INSERT INTO history (user_id, operation_type, stock, shares, price_per_share, total_price, purchase_date) VALUES(?, ?, ?, ?, ?, ?, ?)", session["user_id"], "sale", symbol, shares, price, total, date)

            return redirect("/")

        except ValueError:
            return apology("Invalid number of shares")

        except Exception:
            return apology("Coudn't process you request")

        # If user reached route via GET
    else:
        rows = db.execute("SELECT DISTINCT stock FROM purchase WHERE buyer_id = ?", session["user_id"])

        if len(rows) == 0:
            return render_template("new.html")
        return render_template("sell.html", rows=rows)