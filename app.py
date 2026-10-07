"""VulnShop : boutique de démonstration pour la formation DevSecOps.

ATTENTION : application volontairement vulnérable, à usage pédagogique uniquement.
Ne jamais la déployer ailleurs que dans le pipeline de formation.
"""
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB = "shop.db"


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.executescript(
        """
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS orders;
        CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, name TEXT);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, owner INTEGER, item TEXT, total REAL);
        INSERT INTO users VALUES (1, 'alice@example.com', 'Alice'), (2, 'bob@example.com', 'Bob');
        INSERT INTO orders VALUES (1043, 1, 'Clavier', 49.9), (1044, 2, 'Ecran', 189.0);
        """
    )
    conn.commit()


@app.get("/")
def home():
    return "VulnShop - application volontairement vulnerable (formation DevSecOps)"


@app.get("/users")
def find_user():
    email = request.args.get("email", "")
    # FAILLE VOLONTAIRE (A05 Injection) : requête construite par concaténation.
    # query = "SELECT id, email, name FROM users WHERE email = '" + email + "'"
    query = "SELECT id, email, name FROM users WHERE email = ?"
    # rows = db().execute(query).fetchall()
    rows = db().execute(query, (email,)).fetchall()
    return jsonify([dict(r) for r in rows])


@app.get("/orders/<int:order_id>")
def get_order(order_id):
    # FAILLE VOLONTAIRE (A01 / API1 BOLA) : aucune vérification du propriétaire.
    row = db().execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row))


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000)
