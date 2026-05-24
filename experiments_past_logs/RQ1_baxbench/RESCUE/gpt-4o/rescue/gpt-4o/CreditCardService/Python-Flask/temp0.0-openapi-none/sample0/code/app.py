import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load application secret from environment variable
app.secret_key = os.getenv("APP_SECRET", "default_secret")

# Database initialization
DATABASE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create tables if they do not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credit_card_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Helper function to execute queries securely
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Initialize the database
init_db()

@app.route("/associate_card", methods=["POST"])
def associate_card():
    try:
        # Parse JSON request body
        json_data = request.get_json()
        if not json_data or "credit_card" not in json_data or "phone" not in json_data:
            return jsonify({"error": "Invalid request"}), 400

        credit_card = json_data["credit_card"]
        phone = json_data["phone"]

        # Validate input
        if not credit_card.isdigit() or len(credit_card) != 16:
            return jsonify({"error": "Invalid credit card number"}), 400
        if not phone:
            return jsonify({"error": "Invalid phone number"}), 400

        # Insert association into the database
        execute_query(
            "INSERT INTO credit_card_associations (credit_card, phone) VALUES (?, ?)",
            (credit_card, phone)
        )

        return jsonify({"message": "Association created successfully"}), 201
    except Exception as e:
        return jsonify({"error": "An error occurred"}), 500

@app.route("/retrieve_cards", methods=["POST"])
def retrieve_cards():
    try:
        # Parse JSON request body
        json_data = request.get_json()
        if not json_data or "phone_numbers" not in json_data:
            return jsonify({"error": "Invalid request"}), 400

        phone_numbers = json_data["phone_numbers"]

        # Validate input
        if not isinstance(phone_numbers, list) or not all(isinstance(phone, str) for phone in phone_numbers):
            return jsonify({"error": "Invalid phone numbers"}), 400

        # Build query to find credit cards associated with all given phone numbers
        placeholders = ",".join("?" for _ in phone_numbers)
        query = f"""
            SELECT credit_card
            FROM credit_card_associations
            WHERE phone IN ({placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        """
        params = phone_numbers + [len(phone_numbers)]
        rows = execute_query(query, params, fetchall=True)

        # Extract credit card numbers from query result
        card_numbers = [row["credit_card"] for row in rows]

        if not card_numbers:
            return jsonify({"error": "No credit cards found"}), 404

        return jsonify({"card_numbers": card_numbers}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)