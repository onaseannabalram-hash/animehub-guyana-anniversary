from flask import Flask, render_template, request, redirect, url_for, flash 
import sqlite3
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient   # <-- add this
app = Flask(__name__)   

app = Flask(__name__)
app.secret_key = "animehub_secret_key"  # required for flash messages

DB_NAME = "animehub_project.db"

# --- MongoDB setup ---
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["animehub_project"]
orders_collection = mongo_db["orders"]

PACKAGES = [
    {
        "name": "Anniversary Comic Package",
        "desc": "A limited Edition Comic Book",
        "price": 400,
        "img": "anniv-comic.jpg"
    },
    {
        "name": "Comic Book Package",
        "desc": "Multiple Comic Books",
        "price": 800,
        "img": "comic-pack.jpg"
    },
    {
        "name": "Anniversary Anime Package",
        "desc": "Japanese Comic Books",
        "price": 1500,
        "img": "anime-pack.jpg"
    },
    {
        "name": "Deluxe Package",
        "desc": "A selection of limited Print Comic Books",
        "price": 3000,
        "img": "deluxe.jpg"
    },
    {
        "name": "Mystery Package",
        "desc": "A selection of Comic Books and a T-Shirt",
        "price": 1000,
        "img": "mystery.jpg"
    }
]


SHIPPING = {"North America": 150, "Europe": 200, "Asia": 100, "Guyana": 0}

def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html", packages=PACKAGES)
    
@app.route("/checkout", methods=["POST"])
def checkout():
    name = request.form["customer_name"]
    address = request.form["delivery_address"]
    region = request.form["region"]
    package_name = request.form["package_name"]
    package_price = int(request.form["package_price"])
    shipping_cost = SHIPPING.get(region, 0)
    total = package_price + shipping_cost

    with get_conn() as conn:
        cur = conn.cursor()
        # Ensure table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                delivery_address TEXT,
                region TEXT,
                package_name TEXT,
                package_price INTEGER,
                shipping_cost INTEGER,
                total_price INTEGER,
                created_at TEXT
            )
        """)
        # Insert new order
        cur.execute("""
            INSERT INTO orders (
                customer_name, delivery_address, region,
                package_name, package_price, shipping_cost,
                total_price, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, address, region, package_name,
            package_price, shipping_cost, total,
            datetime.utcnow().isoformat()
        ))
        order_id = cur.lastrowid

    # Mirror to MongoDB (AFTER SQLite insert)
    orders_collection.insert_one({
        "order_id": order_id,
        "customer_name": name,
        "delivery_address": address,
        "region": region,
        "package_name": package_name,
        "package_price": package_price,
        "shipping_cost": shipping_cost,
        "total_price": total,
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    })

    return redirect(url_for("success", order_id=order_id))

   
@app.route("/success/<int:order_id>")
def success(order_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        order = cur.fetchone()
    return render_template("order_success.html", order=order)

@app.route("/orders")
def view_orders():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders")
        orders = cur.fetchall()
    return render_template("view_orders.html", orders=orders)

@app.route("/orders/<int:order_id>/edit", methods=["GET", "POST"])
def edit_order(order_id):
    with get_conn() as conn:
        cur = conn.cursor()
        if request.method == "POST":
            new_address = request.form["delivery_address"]
            new_region = request.form["region"]
            new_package_name = request.form["package_name"]

            # Look up package price from PACKAGES list
            package = next((p for p in PACKAGES if p["name"] == new_package_name), None)
            new_package_price = package["price"] if package else 0

            # Recalculate shipping + total
            new_shipping_cost = SHIPPING.get(new_region, 0)
            new_total = new_package_price + new_shipping_cost

            cur.execute("""
                UPDATE orders
                SET delivery_address=?, region=?, package_name=?, package_price=?, shipping_cost=?, total_price=?
                WHERE id=?
            """, (new_address, new_region, new_package_name, new_package_price, new_shipping_cost, new_total, order_id))
            conn.commit()
            
            # --- Mirror update to MongoDB ---
            orders_collection.update_one(
                {"order_id": order_id},
                {"$set": {
                    "delivery_address": new_address,
                    "region": new_region,
                    "package_name": new_package_name,
                    "package_price": new_package_price,
                    "shipping_cost": new_shipping_cost,
                    "total_price": new_total
                }}
            )

            flash("Order updated successfully.")
            return redirect(url_for("view_orders"))

        cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        order = cur.fetchone()

    return render_template("edit_order.html", order=order, packages=PACKAGES)

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                delivery_address TEXT NOT NULL,
                region TEXT NOT NULL,
                package_name TEXT NOT NULL,
                package_price INTEGER NOT NULL,
                shipping_cost INTEGER NOT NULL,
                total_price INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """)
        conn.commit()
        
@app.route("/orders/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()
        flash("Order cancelled successfully.")
        # Mirror to MongoDB
        orders_collection.update_one(
        {"order_id": order_id},
        {"$set": {"status": "canceled"}}
)
    return redirect(url_for("view_orders"))
    
@app.route('/')
def home():
    return render_template('home.html')  # or whatever your homepage template is



if __name__ == "__main__":
    init_db()   # ensure table exists before app runs
    app.run(debug=True)

